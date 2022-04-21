"""Manage inbound ON command from device."""
from ...topics import ON_FAST
from .broadcast_command import BroadcastCommandHandlerBase


class OnFastInbound(BroadcastCommandHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address, group):
        """Init the OnFastInbound class."""
        super().__init__(topic=ON_FAST, address=address, group=group)

    def _handle_message_received(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF command from a device."""
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xFF)
