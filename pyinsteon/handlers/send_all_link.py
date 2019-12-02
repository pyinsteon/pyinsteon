"""Send a Start All-Linking command."""
from .outbound_base import OutboundHandlerBase
from ..topics import SEND_ALL_LINK_COMMAND
from ..constants import AllLinkMode
from . import ack_handler


class SendAllLinkingCommandHandler(OutboundHandlerBase):
    """Handle Start All-LInking commands."""

    def __init__(self):
        """Init the StartAllLinking class."""
        super().__init__(SEND_ALL_LINK_COMMAND)

    # pylint: disable=arguments-differ
    def send(self, group: int = 0, mode: AllLinkMode = AllLinkMode.CONTROLLER):
        """Send the Start All-Linking message."""
        super().send(group=group, mode=mode)

    # pylint: disable=arguments-differ
    async def async_send(
        self, group: int = 0, mode: AllLinkMode = AllLinkMode.CONTROLLER
    ) -> bool:
        """Send the Start All-Linking message asyncronously."""
        return await super().async_send(group=group, mode=mode)

    @ack_handler(wait_response=False)
    def handle_ack(self, group, mode):
        """Handle the message ACK returning True to the async_send method."""
