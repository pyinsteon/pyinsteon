"""Assign a device to an all link group."""
from ...topics import DELETE_FROM_ALL_LINK_GROUP
from .broadcast_command import BroadcastCommandHandlerBase
from .. import broadcast_handler
from ...address import Address


class DeleteFromAllLinkGroupCommand(BroadcastCommandHandlerBase):
    """Delete From All-Link Group command handler."""

    def __init__(self, address: Address):
        """Init the DeleteFromAllLinkGroupCommand class."""
        super().__init__(address, DELETE_FROM_ALL_LINK_GROUP)

    @broadcast_handler
    def receive_id(self, cmd1, cmd2, target, user_data):
        """Receive the device ID information."""
        cat = target.high
        subcat = target.middle
        firmware = target.low
        self._call_subscribers(address=self._address, cat=cat, subcat=subcat,
                               firmware=firmware, group=cmd2, mode=None)
