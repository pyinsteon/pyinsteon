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
    def receive_record(self, flags: AllLinkRecordFlags, group: int,
                       address: Address, data1: int, data2: int, data3: int):
        """Recieve an all link record."""
        flag_byte = bytes(flags)
        self._call_subscribers(flags=flag_byte, group=group, address=address,
                               data1=data1, data2=data2, data3=data3)
