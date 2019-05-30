"""Manage outbound ON command to a device."""

from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import ON

class OnLevelCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, ON)

    #pylint: disable=arguments-differ
    def send(self, on_level=0xff, group=0):
        """Send the ON command."""
        super().send(on_level=on_level, group=group)

    #pylint: disable=arguments-differ
    async def async_send(self, on_level=0xff, group=0x00):
        """Send the ON command async."""
        return await super().async_send(on_level=on_level, group=group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd2, target, user_data):
        """Handle the ON response direct ACK."""
        group = 1
        if user_data:
            group = user_data.get('d1')
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xff, group=group)
