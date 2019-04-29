"""Manage outbound ON command to a device."""

from .. import status_handler
from .direct_command import DirectCommandHandlerBase
from ...topics import STATUS_REQUEST

class StatusRequestCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, STATUS_REQUEST)

    #pylint: disable=arguments-differ
    def send(self):
        """Send the ON command."""
        super().send()

    #pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send()

    @status_handler
    def handle_response(self, cmd2, target, user_data):
        """Handle the ON response direct ACK."""
        self._call_subscribers(status=cmd2)
