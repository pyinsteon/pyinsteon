"""Manage outbound ON command to a device."""
from . import direct_ack_handler
from .direct_command import DirectCommandHandlerBase
from ..topics import OFF

class OffCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(address, OFF)

    @direct_ack_handler
    def handle_response(self, cmd2, target, user_data):
        """Handle the ON response direct ACK."""
        for listener in self._subscribers:
            listener(on_level=0)
