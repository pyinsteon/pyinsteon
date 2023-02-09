"""Cancel All-Linking."""
from . import ack_handler, nak_handler
from ..topics import CANCEL_ALL_LINKING
from .outbound_base import OutboundHandlerBase


# pylint: disable=arguments-differ
class CancelAllLinkingCommandHandler(OutboundHandlerBase):
    """Cancel All-Linking Command."""

    def __init__(self):
        """Init the CancelAllLinkingCommandHandler class."""
        super().__init__(topic=CANCEL_ALL_LINKING)

    @ack_handler
    async def async_handle_ack(self):
        """Handle the ACK response from the modem."""
        return await self._async_handle_ack()

    @nak_handler
    async def async_handle_nak(self):
        """Handle the ACK response from the modem."""
        return await self._async_handle_nak()
