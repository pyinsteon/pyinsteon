"""Assign a device to an all link group."""
from ...address import Address
from ...topics import DELETE_FROM_ALL_LINK_GROUP
from .broadcast_command import BroadcastCommandHandlerBase


class DeleteFromAllLinkGroupCommand(BroadcastCommandHandlerBase):
    """Delete From All-Link Group command handler."""

    def __init__(self, address: Address):
        """Init the DeleteFromAllLinkGroupCommand class."""
        super().__init__(topic=DELETE_FROM_ALL_LINK_GROUP, address=address)

    def _handle_message_received(self, cmd1, cmd2, target, user_data, hops_left):
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
            link_mode=None,
        )
