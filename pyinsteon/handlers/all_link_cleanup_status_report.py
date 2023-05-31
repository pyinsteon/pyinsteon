"""Handle All-Link Cleanup Status Reports."""
from . import ack_handler, nak_handler
from ..topics import ALL_LINK_CLEANUP_STATUS_REPORT, MODEM
from .inbound_base import InboundHandlerBase


class AllLinkCleanupStatusReport(InboundHandlerBase):
    """Handle All-Link Cleanup Status Reports."""

    arg_spec = {
        "success": "bool - Indicates if the All-Link Cleanup process succeeded or failed."
    }

    def __init__(self):
        """Init AllLinkCleanupStatusReport class."""
        super().__init__(topic=ALL_LINK_CLEANUP_STATUS_REPORT, address=MODEM)

    @ack_handler
    def success_handler(self):
        """Handle the All-Link Status Report inbound ACK message."""
        self._call_subscribers(success=True)

    @nak_handler
    def failure_handler(self):
        """Handle the All-Link Status Report inbound NAK message."""
        self._call_subscribers(success=False)
