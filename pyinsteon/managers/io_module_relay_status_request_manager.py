"""Manage the IO module status request command."""
import asyncio

from ..address import Address
from ..constants import IOModuleControlCommandSet
from ..handlers.to_device.io_module_control import IoModuleControlCommand
from ..subscriber_base import SubscriberBase
from ..utils import bit_is_set


class IoModuleRelayStatusRequestManager(SubscriberBase):
    """Manage the IO module status request command."""

    def __init__(self, address):
        """Init the IoModuleStatusRequestManager class."""
        self._address = Address(address)
        self._command = IoModuleControlCommand(self._address)
        self._command.subscribe(self._handle_status_response)
        self._active_lock = asyncio.Lock()

    async def async_send(self):
        """Send a status command."""
        async with self._active_lock:
            return await self._command.async_send(
                command=IOModuleControlCommandSet.STATUS_REQUEST
            )

    def _handle_status_response(self, result):
        """Handle the status request results."""
        if not self._active_lock.locked():
            return
        relay_status = {}
        for bit in range(0, 8):
            relay_status[bit + 1] = bit_is_set(result, bit)

        self._call_subscribers(relay_status=relay_status)
