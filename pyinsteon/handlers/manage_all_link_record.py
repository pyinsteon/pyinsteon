"""Command handler for message ID 0x6f Manage All-Link Record."""
from . import ack_handler, nak_handler
from ..address import Address
from ..constants import ManageAllLinkRecordAction
from ..protocol.messages.all_link_record_flags import create
from ..topics import MANAGE_ALL_LINK_RECORD
from .outbound_base import OutboundHandlerBase


class ManageAllLinkRecordCommand(OutboundHandlerBase):
    """Command handler for message ID 0x6F Manage All-Link Record."""

    def __init__(self):
        """Init the ManageAllLinkRecordCommand class."""
        super().__init__(topic=MANAGE_ALL_LINK_RECORD)

    # pylint: disable=arguments-differ
    async def async_send(
        self,
        action: ManageAllLinkRecordAction,
        controller: bool,
        group: int,
        target: Address,
        data1: int = 0,
        data2: int = 0,
        data3: int = 0,
        in_use: bool = True,
        high_water_mark: bool = False,
        bit5: bool = True,
        bit4: bool = False,
    ):
        """Send Manage All-Link Record command."""
        flags = create(
            in_use=in_use,
            controller=controller,
            hwm=high_water_mark,
            bit5=bit5,
            bit4=bit4,
        )
        return await super().async_send(
            action=action,
            flags=flags,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )

    @ack_handler()
    def handle_ack(self, action, flags, group, target, data1, data2, data3):
        """Handle ACK response."""

    @nak_handler
    def handle_nak(self, action, flags, group, target, data1, data2, data3):
        """Handle NAK response."""
