"""Manage inbound ON command from device."""
from ...topics import STOP_MANUAL_CHANGE
from .. import broadcast_handler
from .broadcast_command import BroadcastCommandHandlerBase


class ManualChangeInbound(BroadcastCommandHandlerBase):
    """Stop Manual Change command inbound."""

    def __init__(self, address, group):
        """Init the OffInbound class."""
        super().__init__(topic=STOP_MANUAL_CHANGE, address=address, group=group)

    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF command from a device."""
        if not self.is_first_message(target, hops_left):
            return
        self._call_subscribers()
