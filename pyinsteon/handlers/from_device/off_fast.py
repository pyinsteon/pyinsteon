"""Manage inbound ON command from device."""
from .. import  broadcast_handler
from .broadcast_command import BroadcastCommandHandlerBase
from ...topics import OFF_FAST


class OffFastInbound(BroadcastCommandHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address):
        """Init the OffInbound class."""
        super().__init__(address, OFF_FAST)

    @broadcast_handler
    def handle_command(self, cmd2, target, user_data):
        """Handle the OFF command from a device."""
        group = 0
        if user_data:
            group = user_data.get('d1')
        self._call_subscribers(on_level=0, group=group)
