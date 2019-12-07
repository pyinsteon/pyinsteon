"""Assign a device to an all link group."""
from ...topics import ASSIGN_TO_ALL_LINK_GROUP
from .broadcast_command import BroadcastCommandHandlerBase
from .. import broadcast_handler
from ...address import Address


class AssignToAllLinkGroupCommand(BroadcastCommandHandlerBase):
    """Assign to All-Link Group command handler."""

    def __init__(self, address: Address):
        """Init the AssignToAllLinkGroupCommand class."""
        self._address = Address(address)
        super().__init__(topic=ASSIGN_TO_ALL_LINK_GROUP, address=self._address)

    @broadcast_handler
    def receive_id(self, cmd1, cmd2, target, user_data):
        """Receive the device ID information."""
        cat = target.high
        subcat = target.middle
        firmware = target.low
        self._call_subscribers(
            address=self._address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            group=cmd2,
            mode=None,
        )
