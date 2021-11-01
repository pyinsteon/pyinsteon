"""Manage outbound Png command to a device."""
from ...topics import PING
from .. import direct_ack_handler
from .direct_command import DirectCommandHandlerBase


class PingCommand(DirectCommandHandlerBase):
    """Manage an outbound Ping command to a device."""

    def __init__(self, address):
        """Init the PingCommand class."""
        super().__init__(topic=PING, address=address)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the ping response direct ACK."""
        self._call_subscribers()
        super().handle_direct_ack(cmd1, cmd2, target, user_data, hops_left)
