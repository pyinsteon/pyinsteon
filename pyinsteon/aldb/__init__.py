"""Insteon All-Link Database."""
from typing import Callable

from ..address import Address
from .aldb_status import ALDBStatus
from .aldb_version import ALDBVersion
from .aldb_record import ALDBRecord
from .. import pub


class ALDB():
    """Represents a device All-Link database."""

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0fff):
        """Instantiate the ALL-Link Database object."""
        self._records = {}
        self._status = ALDBStatus.EMPTY
        self._prior_status = self._status
        self._version = version

        self._address = address
        self._mem_addr = mem_addr
        self._handlers = {}

        self._register_handlers()

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return len(self._records)

    def __iter__(self):
        """Iterate through each ALDB device record."""
        for key in self._records:
            yield key

    def __getitem__(self, mem_addr):
        """Fetch a device from the ALDB."""
        return self._records.get(mem_addr)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._records[mem_addr] = record

        # After we add a record test load status
        if self._test_loaded():
            self._status = ALDBStatus.LOADED
        elif len(self._records):
            self._status = ALDBStatus.PARTIAL
        else:
            self._status = ALDBStatus.EMPTY

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ', '.join("%s: %r" % item for item in attrs.items())

    @property
    def address(self) -> Address:
        """Returnt the status of the device."""
        return self._address

    @property
    def status(self) -> ALDBStatus:
        """Return the ALDB load status."""
        return self._status

    @property
    def version(self) -> ALDBVersion:
        """Return the ALDB version."""
        return self._version

    @property
    def first_mem_addr(self):
        """Return the expected memory address of the first record."""
        return self._mem_addr

    def get(self, mem_addr):
        """Get the record at address 'mem_addr'."""
        return self._records.get(mem_addr)

    def load(self, refresh=False):
        """Load the All-Link Database."""
        self._handlers['load'].read()

    @property
    def is_loaded(self) -> bool:
        """Test if the ALDB is loaded."""
        return self._status == ALDBStatus.LOADED

    def _add_record(self, record: ALDBRecord):
        """Add a new record to the ALDB"""
        self._records[record.mem_addr] = record

    def _subscribe_topcis(self):
        """Subscribe to topics."""

    def _register_handlers(self):
        """Add all command handlers to the ALDB."""
        from .commands.get_set_all_link_record import GetSetAllLinkRecord
        self._handlers['load'] = GetSetAllLinkRecord(self)

    def _test_loaded(self):
        """Test if the ALDB is fully loaded."""
        has_first = False
        has_last = False
        has_all = False
        last_addr = 0x0000
        for mem_addr in sorted(self._records, reverse=True):
            if mem_addr == self._mem_addr:
                has_first = True
            if self._records[mem_addr].control_flags.is_high_water_mark:
                has_last = True
            if last_addr != 0x0000:
                has_all = (last_addr - mem_addr) == 8
            last_addr = mem_addr
        return has_first and has_all and has_last


class ModemALDB(ALDB):
    """All-Link database for modems."""

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0000):
        """Init the ModemALDB."""
        super().__init__(address, version, mem_addr)
        self._get_next_record_cmd: Callable

    def _register_handlers(self):
        """Add all command handlers to the ALDB."""
        from ..aldb.commands.modem_get_first_record import GetFirstRecord
        from .commands.modem_all_link_record_response import AllLinkRecordResponse
        self._handlers['load'] = GetFirstRecord(self._address)
        self._handlers['rec_resp'] = AllLinkRecordResponse(self._address,
                                                           self._add_record)
