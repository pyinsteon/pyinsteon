"""Receive an All-Link record."""

from typing import Callable

from ... import pub
from ...messages.all_link_record_flags import AllLinkRecordFlags
from ..aldb_record import ALDBRecord
from ...address import Address


class AllLinkRecordResponse():
    """Receive an All-Link record."""

    def __init__(self, address: Address, add_record_method: Callable):
        """Init the AllLinkRecordResponse class."""
        self._address = address
        self._add_record_method = add_record_method
        self._record_id = 0x0fff
        pub.subscribe(self.receive_record, 'all_link_record_response')

    def receive_record(self, flags: AllLinkRecordFlags, group: int,
                       address: Address, data1: int, data2: int, data3: int):
        """Recieve an all link record."""
        self._record_id -= 8
        record = ALDBRecord(self._record_id, flags, group, address,
                            data1, data2, data3)
        self._add_record_method(record)
        pub.sendMessage('modem.aldb.get_next_record')
