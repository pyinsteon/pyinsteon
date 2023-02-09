"""Send a Start All-Linking command."""
from . import ack_handler, nak_handler
from ..topics import SEND_ALL_LINK_COMMAND
from .outbound_base import OutboundHandlerBase


class SendAllLinkCommandHandler(OutboundHandlerBase):
    """Handle Start All-LInking commands."""

    def __init__(self):
        """Init the StartAllLinking class."""
        super().__init__(SEND_ALL_LINK_COMMAND)

    # pylint: disable=arguments-differ
    async def async_send(self, group: int, cmd1: int, cmd2: int) -> bool:
        """Send the Start All-Linking message asyncronously."""
        return await super().async_send(group=group, cmd1=cmd1, cmd2=cmd2)

    @ack_handler
    async def async_handle_ack(self, group, cmd1, cmd2):
        """Handle the ACK response."""
        await self._async_handle_ack()

    @nak_handler
    async def async_handle_nak(self, group, cmd1, cmd2):
        """Handle the NAK response."""
        await self._async_handle_nak()
