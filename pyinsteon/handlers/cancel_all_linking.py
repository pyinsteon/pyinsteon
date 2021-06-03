"""Cancel All-Linking."""
from ..topics import CANCEL_ALL_LINKING
from .outbound_base import OutboundHandlerBase


# pylint: disable=arguments-differ
class CancelAllLinkingCommandHandler(OutboundHandlerBase):
    """Cancel All-Linking Command."""

    def __init__(self):
        """Init the CancelAllLinkingCommandHandler class."""
        super().__init__(topic=CANCEL_ALL_LINKING)
