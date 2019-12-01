"""Manage inbound OFF All-Link Cleanup command to a device."""

from .. import inbound_handler
from .all_link_cleanup_command import AllLinkCleanupCommandHandlerBase
from ...topics import OFF


class OffAllLinkCleanupInbound(AllLinkCleanupCommandHandlerBase):
    """Off All-Link Cleanup command inbound."""

    def __init__(self, address, group):
        """Init the OffAllLinkCleanupAckInbound class."""
        super().__init__(address, group, OFF)

    @inbound_handler
    def handle_command(self, cmd1, cmd2, target, user_data):
        """Handle the ON All-Link Cleanup from a device."""
        self._call_subscribers()
