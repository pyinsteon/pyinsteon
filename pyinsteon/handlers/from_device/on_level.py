"""Manage outbound ON command to a device."""

from ...topics import ON
from .. import broadcast_handler
from .broadcast_command import BroadcastCommandHandlerBase


class OnLevelInbound(BroadcastCommandHandlerBase):
    """On Level command inbound."""

    def __init__(self, address, group):
        """Init the OnLevelInbound class."""
        super().__init__(topic=ON, address=address, group=group)

    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the ON command from a device."""
        if not self.is_first_message(target, hops_left):
            return
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xFF)
