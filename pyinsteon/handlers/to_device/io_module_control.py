"""Manage outbound ON command to a device."""

from ...constants import IOModuleControlCommandSet
from ...topics import IO_MODULE_CONTROL
from .direct_command import DirectCommandHandlerBase


class IoModuleControlCommand(DirectCommandHandlerBase):
    """Manage an outbound IO_MODULE_CONTROL command to a device."""

    def __init__(self, address):
        """Init the IoModuleControlCommand class."""
        super().__init__(topic=IO_MODULE_CONTROL, address=address)
        self._is_status = False

    # pylint: disable=arguments-differ
    async def async_send(self, command: IOModuleControlCommandSet):
        """Send the ON command async."""
        return await super().async_send(command=command)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        # Send cmd2 back because when the command is STATUS_REQUEST the result in in cmd2
        self._call_subscribers(result=cmd2)
