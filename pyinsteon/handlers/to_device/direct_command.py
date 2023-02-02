"""Handle an outbound direct message to a device."""

from abc import ABCMeta
import asyncio

import async_timeout

from .. import ack_handler, direct_ack_handler, direct_nak_handler, nak_handler
from ...constants import MessageFlagType, ResponseStatus
from ..outbound_base import OutboundHandlerBase

TIMEOUT = 6  # Wait time for device response


class DirectCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound direct message handling."""

    __meta__ = ABCMeta

    def __init__(self, topic, address, group=None, message_type=MessageFlagType.DIRECT):
        """Init the DirectCommandHandlerBase class."""
        self._response_lock = asyncio.Lock()
        self._direct_response = asyncio.Queue()
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
                async with async_timeout.timeout(TIMEOUT + 0.1):
                    return await self._message_response.get()
            except asyncio.TimeoutError:
                pass
        return ResponseStatus.FAILURE

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle Direct Command ACK message."""
        await self._async_handle_ack()
        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self._response_lock:
                    direct_response = await self._direct_response.get()
                    await self._message_response.put(direct_response)
        except asyncio.TimeoutError:
            await self._message_response.put(ResponseStatus.DEVICE_UNRESPONSIVE)

    @nak_handler
    async def async_handle_nak(self, cmd1, cmd2, user_data):
        """Handle the NAK response from the modem."""
        await self._async_handle_nak()

    @direct_nak_handler
    async def async_handle_direct_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the message ACK."""
        await asyncio.sleep(0.05)
        try:
            response = ResponseStatus(cmd2)
        except ValueError:
            response = ResponseStatus.FAILURE
        if self._response_lock.locked():
            await self._direct_response.put(response)
            await asyncio.sleep(0.05)
            self._update_subscribers_on_direct_nak(
                cmd1, cmd2, target, user_data, hops_left
            )
            await asyncio.sleep(0.05)

    @direct_ack_handler
    async def async_handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK."""
        # Need to make sure the ACK has time to aquire the lock
        await asyncio.sleep(0.05)
        if self._response_lock.locked():
            await self._direct_response.put(ResponseStatus.SUCCESS)
            self._update_subscribers_on_direct_ack(
                cmd1, cmd2, target, user_data, hops_left
            )
            await asyncio.sleep(0.05)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on NAK received."""

    def _update_subscribers_on_direct_nak(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers on DIRECT NAK received."""
