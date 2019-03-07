"""Receive an All-Link record."""

import logging

from ... import pub
from ...messages.all_link_record_flags import AllLinkRecordFlags
from ..aldb_record import ALDBRecord
from .. import ModemALDB
from ...address import Address

_LOGGER = logging.getLogger(__name__)

class AllLinkRecordResponse():
    """Receive an All-Link record."""

    def __init__(self, aldb: ModemALDB):
        """Init the AllLinkRecordResponse class."""
        self._aldb = aldb
        self._record_id = 0x0fff
        pub.subscribe(self.receive_record, 'modem.aldb.all_link_record_response')

    def receive_record(self, flags: AllLinkRecordFlags, group: int,
                       address: Address, data1: int, data2: int, data3: int):
        """Recieve an all link record."""
        self._record_id -= 8
        record = ALDBRecord(self._record_id, flags, group, address,
                            data1, data2, data3)
        _LOGGER.debug('Modem ALDB Record: %s', record)
        self._aldb[self._record_id] = record
        pub.sendMessage('modem.aldb.get_next_all_link_record')
