"""Manage inbound ON command from device."""
from .. import  broadcast_handler
from .broadcast_command import BroadcastCommandHandlerBase
from ...topics import OFF


class OffInbound(BroadcastCommandHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address, group):
        """Init the OffInbound class."""
        super().__init__(address, OFF)
        # put the following commands in a subclass!
        self._group = group

    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data):
        """Handle the OFF command from a device."""
        group = target.low
        if group == self._group:
            self._call_subscribers(on_level=0)
