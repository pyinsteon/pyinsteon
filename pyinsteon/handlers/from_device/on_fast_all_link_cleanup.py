"""Manage inbound OFF All-Link Cleanup command to a device."""

from ...topics import ON_FAST
from .. import inbound_handler
from .all_link_cleanup_command import AllLinkCleanupCommandHandlerBase


class OnFastAllLinkCleanupInbound(AllLinkCleanupCommandHandlerBase):
    """Off All-Link Cleanup command inbound."""

    def __init__(self, address, group):
        """Init the OffAllLinkCleanupAckInbound class."""
        super().__init__(topic=ON_FAST, address=address, group=group)

    @inbound_handler
    def handle_command(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the ON_FAST All-Link Cleanup from a device."""
        self._call_subscribers()
