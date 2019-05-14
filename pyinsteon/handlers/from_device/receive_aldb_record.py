"""Handle sending a read request for ALDB records."""
import logging
from ..inbound_base import InboundHandlerBase
from ...topics import EXTENDED_READ_WRITE_ALDB
from .. import inbound_handler
from ...address import Address


_LOGGER = logging.getLogger(__name__)


class ReceiveALDBRecordHandler(InboundHandlerBase):
    """Receive an ALDB record direct inbound message."""

    def __init__(self, address: Address):
        """Init the ReceiveALDBRecordHandler class."""
        topic = '{}.{}.direct'.format(address.id, EXTENDED_READ_WRITE_ALDB)
        super().__init__(topic)

    @inbound_handler
    def handle_response(self, cmd2, target, user_data):
        """Handle the inbound message."""
        from ...aldb.aldb_record import create_from_userdata
        _LOGGER.debug('ALDB Read direct message received')
        if user_data:
            is_response = user_data['d2'] == 0x01
            record = create_from_userdata(user_data)
            self._call_subscribers(is_response=is_response, record=record)
