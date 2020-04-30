"""Send a Start All-Linking command."""
from .send_all_link import SendAllLinkCommandHandler


class SendAllLinkOffCommandHandler(SendAllLinkCommandHandler):
    """Send Start All-LInking ON commands."""

    # pylint: disable=arguments-differ
    async def async_send(self, group: int):
        """Send the Start All-Linking message asyncronously."""
        return await super().async_send(group=group, cmd1=0x13, cmd2=0x00)
