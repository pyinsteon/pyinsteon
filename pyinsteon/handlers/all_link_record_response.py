"""Receive an All-Link record for an Insteon Modem."""

import logging

from .inbound_base import InboundHandlerBase
from ..address import Address
from ..topics import ALL_LINK_RECORD_RESPONSE
from . import inbound_handler
from ..protocol.messages.all_link_record_flags import AllLinkRecordFlags

_LOGGER = logging.getLogger(__name__)


class AllLinkRecordResponseHandler(InboundHandlerBase):
    """Receive an All-Link record for an Insteon Modem."""

    def __init__(self):
        """Init the AllLinkRecordResponse class."""
        super().__init__(ALL_LINK_RECORD_RESPONSE)

    @inbound_handler
    def receive_record(
        self,
        flags: AllLinkRecordFlags,
        group: int,
        target: Address,
        data1: int,
        data2: int,
        data3: int,
    ):
        """Recieve an all link record."""
        from ..constants import AllLinkMode

        controller = flags.mode == AllLinkMode.CONTROLLER
        self._call_subscribers(
            in_use=flags.is_in_use,
            high_water_mark=flags.is_hwm,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            bit5=flags.is_bit_5_set,
            bit4=flags.is_bit_4_set,
        )
