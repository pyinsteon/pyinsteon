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

    def send(self, link_mode: AllLinkMode, group: int = 0):
        """Send the Start All-Linking Command."""
        super().send(link_mode=link_mode, group=group)

    async def async_send(self, link_mode: AllLinkMode, group: int = 0):
        """Send the Start All-Linking Command."""
        return await super().async_send(link_mode=link_mode, group=group)

    @ack_handler
    def handle_ack(self, link_mode: AllLinkMode, group: int):
        """Handle the ACK message."""
        super().handle_ack(link_mode=link_mode, group=group)
