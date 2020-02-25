"""Start All-Linking."""
from . import ack_handler
from ..constants import AllLinkMode
from ..topics import START_ALL_LINKING
from .outbound_base import OutboundHandlerBase


# pylint: disable=arguments-differ
class StartAllLinkingCommandHandler(OutboundHandlerBase):
    """Start All-Linking Command."""

    def __init__(self):
        """Init the StartAllLinkingCommandHandler class."""
        super().__init__(topic=START_ALL_LINKING)

    def send(self, mode: AllLinkMode, group: int = 0):
        """Send the Start All-Linking Command."""
        super().send(mode=mode, group=group)

    async def async_send(self, mode: AllLinkMode, group: int = 0):
        """Send the Start All-Linking Command."""
        return await super().async_send(mode=mode, group=group)

    @ack_handler()
    def handle_ack(self, mode: AllLinkMode, group: int):
        """Handle the ACK message."""
