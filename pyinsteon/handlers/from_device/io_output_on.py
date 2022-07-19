"""Manage outbound ON command to a device."""

from ...topics import IO_OUTPUT_ON
from .broadcast_command import BroadcastCommandHandlerBase


class IoOutputOnInbound(BroadcastCommandHandlerBase):
    """IO Output On command inbound."""

    def __init__(self, address):
        """Init the IoOutputOnInbound class."""
        super().__init__(topic=IO_OUTPUT_ON, address=address)

    def _handle_message_received(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the ON command from a device."""
        self._call_subscribers(output=cmd2, on_level=0xFF)
