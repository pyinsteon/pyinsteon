"""Manage inbound ON command from device."""
from .. import  broadcast_handler
from .broadcast_command import BroadcastCommandHandlerBase
from ...topics import ON_FAST


class OnFastInbound(BroadcastCommandHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address, group):
        """Init the OnFastInbound class."""
        super().__init__(address, ON_FAST)
        # put the following commands in a subclass!
        self._group = group


    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data):
        """Handle the OFF command from a device."""
        group = target.low
        if group == self._group:
            self._call_subscribers(on_level=cmd2 if cmd2 else 0xff)
