"""Manage outbound ON command to a device."""

from .. import inbound_handler
from .all_link_cleanup_ack_command  import AllLinkCleanupAckCommandHandlerBase
from ...topics import ON


class OnLevelAllLinkCleanupAckInbound(AllLinkCleanupAckCommandHandlerBase):
    """On Level All-Link Cleanup command inbound."""

    def __init__(self, address):
        """Init the OnLevelInbound class."""
        super().__init__(address, ON)

    @inbound_handler
    def handle_command(self, cmd1, cmd2, target, user_data):
        """Handle the ON All-Link Cleanup from a device."""
        self._call_subscribers(cmd1=cmd1, group=cmd2)
