"""Handle All-Link Cleanup Status Reports."""
from ..topics import ALL_LINK_CLEANUP_STATUS_REPORT
from .outbound_base import OutboundHandlerBase
from . import ack_handler, nak_handler


class AllLinkCleanupStatusReport(OutboundHandlerBase):
    """Handle All-Link Cleanup Status Reports."""

    def __init__(self):
        """Init AllLinkCleanupStatusReport class."""
        super().__init__(topic=ALL_LINK_CLEANUP_STATUS_REPORT)

    @ack_handler
    def handle_ack(self):
        """Handle an ACK response."""

    @nak_handler
    def handle_nak(self):
        """Handle a NAK response."""
