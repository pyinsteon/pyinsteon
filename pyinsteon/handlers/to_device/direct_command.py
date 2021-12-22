"""Handle an outbound direct message to a device."""

import asyncio
from abc import ABCMeta

import async_timeout

from ...constants import MessageFlagType, ResponseStatus
from .. import ack_handler, direct_ack_handler, direct_nak_handler
from ..outbound_base import OutboundHandlerBase

TIMEOUT = 3  # Wait time for device response


class DirectCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound direct message handling."""

    __meta__ = ABCMeta

    def __init__(self, topic, address, group=None, message_type=MessageFlagType.DIRECT):
        """Init the DirectCommandHandlerBase class."""
        self._response_lock = asyncio.Lock()
        super().__init__(topic, address=address, group=group, message_type=message_type)

    @property
    def response_lock(self) -> asyncio.Lock:
        """Lock to manage the response between ACK and Direct ACK."""
        return self._response_lock

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        ack_response = await super().async_send(address=self._address, **kwargs)
        if ack_response == ResponseStatus.SUCCESS:
            try:
                async with async_timeout.timeout(TIMEOUT):
                    async with self._response_lock:
                        return await self._message_response.get()
            except asyncio.TimeoutError:
                # return ResponseStatus.DEVICE_UNRESPONSIVE
                pass
        return ResponseStatus.FAILURE

    # pylint: disable=arguments-differ
    @ack_handler
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle Direct Command ACK message."""
        return super().handle_ack()

    @direct_nak_handler
    def handle_direct_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the message ACK."""
        if not self._response_lock.locked():
            return
        self._message_response.put_nowait(ResponseStatus.UNCLEAR)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK."""
        if not self._response_lock.locked():
            return
        self._message_response.put_nowait(ResponseStatus.SUCCESS)
