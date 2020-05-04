"""Manage inbound ON command from device."""
from .. import broadcast_handler
from ...address import Address
from ...topics import STOP_MANUAL_CHANGE
from .broadcast_command import BroadcastCommandHandlerBase


class ManualChangeInbound(BroadcastCommandHandlerBase):
    """Stop Manual Change command inbound."""

    def __init__(self, address, group):
        """Init the OffInbound class."""
        self._address = Address(address)
        self._group = group
        super().__init__(
            topic=STOP_MANUAL_CHANGE, address=self._address, group=self._group
        )

    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF command from a device."""
        self._call_subscribers()
