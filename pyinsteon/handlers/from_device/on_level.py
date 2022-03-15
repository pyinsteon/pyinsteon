"""Manage outbound ON command to a device."""

from ...topics import ON
from .broadcast_command import BroadcastCommandHandlerBase


class OnLevelInbound(BroadcastCommandHandlerBase):
    """On Level command inbound."""

    def __init__(self, address, group):
        """Init the OnLevelInbound class."""
        super().__init__(topic=ON, address=address, group=group)

    def _handle_message_received(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the ON command from a device."""
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xFF)
