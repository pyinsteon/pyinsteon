"""Start All-Linking."""
from ..constants import AllLinkMode
from ..topics import START_ALL_LINKING
from . import ack_handler
from .outbound_base import OutboundHandlerBase


# pylint: disable=arguments-differ
class StartAllLinkingCommandHandler(OutboundHandlerBase):
    """Start All-Linking Command."""

    def __init__(self):
        """Init the StartAllLinkingCommandHandler class."""
        super().__init__(topic=START_ALL_LINKING)

    async def async_send(self, link_mode: AllLinkMode, group: int = 0):
        """Send the Start All-Linking Command."""
        return await super().async_send(link_mode=link_mode, group=group)

    @ack_handler
    async def async_handle_ack(self, link_mode, group):
        """Handle the ACK response."""
        return await super().async_handle_ack()
