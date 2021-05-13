"""Cancel All-Linking."""
from . import ack_handler
from ..topics import CANCEL_ALL_LINKING
from .outbound_base import OutboundHandlerBase


# pylint: disable=arguments-differ
class CancelAllLinkingCommandHandler(OutboundHandlerBase):
    """Cancel All-Linking Command."""

    def __init__(self):
        """Init the CancelAllLinkingCommandHandler class."""
        super().__init__(topic=CANCEL_ALL_LINKING)

    def send(self):
        """Send the Cancel All-Linking Command."""
        super().send()

    async def async_send(self):
        """Send the Cancel All-Linking Command."""
        return await super().async_send()

    @ack_handler()
    def handle_ack(self,):
        """Handle the ACK message."""
