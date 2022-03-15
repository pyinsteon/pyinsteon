"""Manage inbound ON command from device."""
from ...topics import STOP_MANUAL_CHANGE
from .broadcast_command import BroadcastCommandHandlerBase


class ManualChangeInbound(BroadcastCommandHandlerBase):
    """Stop Manual Change command inbound."""

    def __init__(self, address, group):
        """Init the OffInbound class."""
        super().__init__(topic=STOP_MANUAL_CHANGE, address=address, group=group)

    def _handle_message_received(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF command from a device."""
        self._call_subscribers()
