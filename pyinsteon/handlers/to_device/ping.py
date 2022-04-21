"""Manage outbound Png command to a device."""
from ...topics import PING
from .direct_command import DirectCommandHandlerBase


class PingCommand(DirectCommandHandlerBase):
    """Manage an outbound Ping command to a device."""

    def __init__(self, address):
        """Init the PingCommand class."""
        super().__init__(topic=PING, address=address)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers()
