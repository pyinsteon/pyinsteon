"""Manage outbound ON command to a device."""

from .. import broadcast_handler
from .broadcast_command import BroadcastCommandHandlerBase
from ...topics import ON


class OnLevelInbound(BroadcastCommandHandlerBase):
    """On Level command inbound."""

    def __init__(self, address, group):
        """Init the OnLevelInbound class."""
        super().__init__(address, ON)
        # put the following commands in a subclass!
        self._group = group

    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data):
        """Handle the ON command from a device."""
        group = target.low
        if group == self._group:
            self._call_subscribers(on_level=cmd2 if cmd2 else 0xff)
