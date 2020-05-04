"""Manage inbound ON command from device."""
from .. import broadcast_handler
from ...address import Address
from ...topics import ON_FAST
from .broadcast_command import BroadcastCommandHandlerBase


class OnFastInbound(BroadcastCommandHandlerBase):
    """Off Level command inbound."""

    def __init__(self, address, group):
        """Init the OnFastInbound class."""
        self._address = Address(address)
        self._group = group
        super().__init__(topic=ON_FAST, address=self._address, group=self._group)

    @broadcast_handler
    def handle_command(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF command from a device."""
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xFF)
