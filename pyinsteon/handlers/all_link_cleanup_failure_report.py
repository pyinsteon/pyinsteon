"""Handle All-Link Cleanup Status Reports."""
from . import inbound_handler
from ..address import Address
from ..topics import ALL_LINK_CLEANUP_FAILURE_REPORT
from .inbound_base import InboundHandlerBase


class AllLinkCleanupFailureReport(InboundHandlerBase):
    """Handle All-Link Cleanup Failure Reports."""

    arg_spec = {
        "success": "bool - Indicates if the All-Link clean up report succeded or failed.",
        "group": "int - The group number of the All-Link command.",
        "target": "Address - The target device for clean up.",
    }

    def __init__(self):
        """Init AllLinkCleanupFailureReport class."""
        super().__init__(topic=ALL_LINK_CLEANUP_FAILURE_REPORT)

    @inbound_handler
    def handle_inbound(self, error: int, group: int, target: Address):
        """Handle the All-Link Failure Report inbound message."""
        self._call_subscribers(success=False, group=group, target=target)
