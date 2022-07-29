"""Handle an outbound direct message to a device."""

import asyncio
from abc import ABCMeta
from datetime import datetime

import async_timeout

from ...constants import MessageFlagType, ResponseStatus
from .. import ack_handler, direct_ack_handler, direct_nak_handler
from ..outbound_base import OutboundHandlerBase

MIN_DUP = 0.7
MAX_DUP = 2
TIMEOUT = 3  # Wait time for device response


class DirectCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound direct message handling."""

    __meta__ = ABCMeta

    def __init__(self, topic, address, group=None, message_type=MessageFlagType.DIRECT):
        """Init the DirectCommandHandlerBase class."""
        self._response_lock = asyncio.Lock()
        self._direct_response = asyncio.Queue()
        super().__init__(topic, address=address, group=group, message_type=message_type)
        self._last_command = datetime(1, 1, 1)
        self._last_hops_left = None

    @property
    def response_lock(self) -> asyncio.Lock:
        """Lock to manage the response between ACK and Direct ACK."""
        return self._response_lock

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        self._last_command = datetime(1, 1, 1)
        ack_response = await super().async_send(address=self._address, **kwargs)
        if ack_response == ResponseStatus.SUCCESS:
            try:
                async with async_timeout.timeout(TIMEOUT + 0.1):
                    return await self._message_response.get()
            except asyncio.TimeoutError:
                pass
        return ResponseStatus.FAILURE

    # pylint: disable=arguments-differ
    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle Direct Command ACK message."""
        await super().async_handle_ack()
        try:
            async with async_timeout.timeout(TIMEOUT):
                async with self._response_lock:
                    direct_response = await self._direct_response.get()
                    await self._message_response.put(direct_response)
        except asyncio.TimeoutError:
            await self._message_response.put(ResponseStatus.DEVICE_UNRESPONSIVE)

    @direct_nak_handler
    async def async_handle_direct_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the message ACK."""
        await asyncio.sleep(0.05)
        if self._response_lock.locked():
            await self._direct_response.put(ResponseStatus.UNCLEAR)
            self._update_subscribers_on_nak(cmd1, cmd2, target, user_data, hops_left)

    @direct_ack_handler
    async def async_handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK."""
        # Need to make sure the ACK has time to aquire the lock
        await asyncio.sleep(0.05)
        if self._response_lock.locked():
            if not self._is_first_message(hops_left):
                return
            await self._direct_response.put(ResponseStatus.SUCCESS)
            self._update_subscribers_on_ack(cmd1, cmd2, target, user_data, hops_left)
            await asyncio.sleep(0.05)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on NAK received."""

    def _is_first_message(self, hops_left):
        """Test if the message is a duplicate."""
        curr_time = datetime.now()
        tdelta = curr_time - self._last_command
        if tdelta.days > 0:
            delta = 9999
        else:
            delta = tdelta.seconds + tdelta.microseconds / 1000000
        self._last_command = curr_time
        if hops_left == self._last_hops_left and delta < MIN_DUP:
            return False
        if (
            self._last_hops_left is None
            or (hops_left == self._last_hops_left and delta > MIN_DUP)
            or hops_left > self._last_hops_left
            or delta >= MAX_DUP
        ):
            self._last_hops_left = hops_left
            return True
        return False
