"""Manage outbound ON command to a device."""
#pylint: disable=arguments-differ
from .direct_command import DirectCommandHandlerBase
from ..topics import OFF

class OffCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, OFF)

    async def async_send(self):
        """Send the ON command async."""
        return await self._async_send()

    def handle_inbound(self, cmd2, target, user_data):
        """Handle the ON response direct ACK."""
        self._msg_response_queue.put_nowait(True)
        for listener in self._subscribers:
            listener(on_level=0)
