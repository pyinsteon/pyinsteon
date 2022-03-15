"""Handle All-Link Cleanup Status Reports."""
from ..address import Address
from ..topics import ALL_LINK_CLEANUP_FAILURE_REPORT
from . import inbound_handler
from .inbound_base import InboundHandlerBase


class AllLinkCleanupFailureReport(InboundHandlerBase):
    """Handle All-Link Cleanup Failure Reports."""

    def __init__(self):
        """Init AllLinkCleanupFailureReport class."""
        super().__init__(topic=ALL_LINK_CLEANUP_FAILURE_REPORT)

    @inbound_handler
    def handle_inbound(self, error: int, group: int, target: Address):
        """Handle the All-Link Failure Report inbound message."""
        self._call_subscribers(success=False, group=group, target=target)
