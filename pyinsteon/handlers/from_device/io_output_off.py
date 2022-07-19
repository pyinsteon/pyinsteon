"""Manage inbound ON command from device."""
from ...topics import IO_OUTPUT_OFF
from .broadcast_command import BroadcastCommandHandlerBase


class IoOutputOffInbound(BroadcastCommandHandlerBase):
    """IO Output Off command inbound."""

    def __init__(self, address):
        """Init the IoOutputOffInbound class."""
        super().__init__(topic=IO_OUTPUT_OFF, address=address)

    def _handle_message_received(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF command from a device."""
        self._call_subscribers(output=cmd2, on_level=0)
