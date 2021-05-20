"""Handle All-Link Cleanup Status Reports."""
from ..topics import ALL_LINK_CLEANUP_STATUS_REPORT
from . import nak_handler
from .outbound_base import OutboundHandlerBase


class AllLinkCleanupStatusReport(OutboundHandlerBase):
    """Handle All-Link Cleanup Status Reports."""

    def __init__(self):
        """Init AllLinkCleanupStatusReport class."""
        super().__init__(topic=ALL_LINK_CLEANUP_STATUS_REPORT)

    @nak_handler
    def handle_nak(self):
        """Handle a NAK response."""
