"""Manage outbound ON command to a device."""

from .. import direct_ack_handler
from ...topics import ON
from .direct_command import DirectCommandHandlerBase


class OnLevelCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address, group):
        """Init the OnLevelCommand class."""
        super().__init__(topic=ON, address=address, group=group)

    @property
    def group(self):
        """Command group."""
        return self._group

    # pylint: disable=arguments-differ
    def send(self, on_level=0xFF):
        """Send the ON command."""
        super().send(on_level=on_level)

    # pylint: disable=arguments-differ
    async def async_send(self, on_level=0xFF):
        """Send the ON command async."""
        return await super().async_send(on_level=on_level, group=self._group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the ON response direct ACK."""
        if self._response_lock.locked():
            self._call_subscribers(on_level=cmd2 if cmd2 else 0xFF)
