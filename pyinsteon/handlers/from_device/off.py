"""Manage inbound ON command from device."""
from ...topics import OFF
from .. import broadcast_handler
from .broadcast_command import BroadcastCommandHandlerBase


class OffInbound(BroadcastCommandHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address, group):
        """Init the OffInbound class."""
        super().__init__(topic=OFF, address=address, group=group)

    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF command from a device."""
        if not self.is_first_message(target, hops_left):
            return
        self._call_subscribers(on_level=0)
