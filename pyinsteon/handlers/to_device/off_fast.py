"""Manage outbound ON command to a device."""
from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import OFF_FAST


class OffFastCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, OFF_FAST)

    #pylint: disable=arguments-differ
    def send(self, group=0):
        """Send the OFF command."""
        super().send(group=group)

    #pylint: disable=arguments-differ
    async def async_send(self, group=0x00):
        """Send the OFF command async."""
        return await super().async_send(group=group)

    @direct_ack_handler
    def handle_response(self, cmd2, target, user_data):
        """Handle the OFF response direct ACK."""
        group = 0
        if user_data:
            group = user_data.get('d1')
        self._call_subscribers(on_level=0, group=group)
