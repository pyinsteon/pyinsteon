"""Insteon All-Link Database.

The All-Link database contains database records that represent links to other
Insteon devices that either respond to or control the current device.
"""
from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Callable

from ..address import Address
from .aldb_status import ALDBStatus
from .aldb_version import ALDBVersion
from .aldb_record import ALDBRecord
from .. import pub


_LOGGER = logging.getLogger(__name__)

class ALDBBase(ABC):
    """Represents a base class for a device All-Link database."""

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0fff):
        """Instantiate the ALL-Link Database object."""
        self._records = {}
        self._status = ALDBStatus.EMPTY
        self._version = version

        self._address = Address(address)
        self._mem_addr = mem_addr
        self._cb_aldb_loaded = None
        self._read_manager = None

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return len(self._records)

    def __iter__(self):
        """Iterate through each ALDB device record."""
        for key in sorted(self._records, reverse=True):
            yield key

    def __getitem__(self, mem_addr):
        """Fetch a device from the ALDB."""
        return self._records.get(mem_addr)

    @abstractmethod
    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""

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

    def high_water_mark_mem_addr(self):
        """Return the High Water Mark record memory address."""
        for record in self._records:
            if record.control_flags.is_high_water_mark:
                return record.mem_addr
        return None

    @property
    def is_loaded(self) -> bool:
        """Test if the ALDB is loaded."""
        return self._status == ALDBStatus.LOADED

    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return self._records.get(mem_addr, default)

    def load_saved_records(self, status: ALDBStatus, records: [ALDBRecord]):
        """Load All-Link records from a dictionary of saved records."""
        if isinstance(status, ALDBStatus):
            self._status = status
        else:
            self._status = ALDBStatus(status)
        for mem_addr in records:
            record = records[mem_addr]
            self._records[mem_addr] = record
        if self.is_loaded and self._records:
            keys = list(self._records.keys())
            keys.sort(reverse=True)
            self._mem_addr = keys[0]


class ALDB(ALDBBase):
    """All-Link Database for a device."""

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0fff):
        """Init the ALDB class."""
        from ..managers.read_manager import ALDBReadManager
        from ..managers.write_manager import ALDBWriteManager
        super().__init__(address=address, version=version, mem_addr=mem_addr)
        self._read_manager = ALDBReadManager(self)
        self._write_manager = ALDBWriteManager(self)
        self._dirty_records = {}

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._dirty_records[mem_addr] = record

    def load(self, refresh=False, callback: Callable = None):
        """Load the ALDB calling the callback when done."""
        self._cb_aldb_loaded = callback
        asyncio.ensure_future(self.async_load(refresh))

    async def async_load(self, mem_addr: int = 0x00, num_recs: int = 0x00,
                         refresh: bool = False, callback: Callable = None):
        """Load the All-Link Database."""
        _LOGGER.debug('Loading the ALDB async')
        self._status = ALDBStatus.LOADING
        if refresh:
            self._records = {}
        async for rec in self._read_manager.async_read(mem_addr=mem_addr, num_recs=num_recs):
            self._records[rec.mem_addr] = rec
        self._set_load_status()
        if callback:
            callback()
        return self._status

    def write_records(self):
        """Write modified records to the device."""
        if self.is_loaded():
            asyncio.ensure_future(self.async_write_records())

    async def async_write_records(self):
        """Write modified records to the device."""
        completed = []
        for mem_addr in self._dirty_records:
            record = self._dirty_records[mem_addr]
            if record.mem_addr == 0x0000:
                record.mem_addr = self._get_next_mem_addr()
            # We assume a direct ACK is a confirmation of write.
            # Should we re-read to ensure it is correct.
            if await self._write_manager.async_write(record):
                completed.append(record)
                self._records[record.mem_addr] = record
        for record in completed:
            self._dirty_records.pop(record.mem_addr)
        return len(completed)

    def add(self, group: int, target: Address, controller: bool = False,
            data1: int = 0x00, data2: int = 0x00, data3: int = 0x00):
        """Add an All-Link record.

        This method does not write to the device. To write modifications to the device
        use `write_records` or `async_write_records`.
        """
        from .control_flags import ControlFlags
        flags = ControlFlags(in_use=True, controller=controller, used_before=True)
        mem_addr = 0x0000

        rec = ALDBRecord(memory=mem_addr, control_flags=flags, group=group, address=target,
                         data1=data1, data2=data2, data3=data3)
        self._dirty_records[rec.mem_addr] = rec

    def remove(self, mem_addr: int):
        """Remove an All-Link record."""
        from .control_flags import ControlFlags
        rec = self._records.get(mem_addr)
        if not rec:
            raise IndexError('Memory location not found.')
        new_flags = ControlFlags(in_use=False, controller=rec.control_flags.is_controller,
                                 used_before=rec.control_flags.is_used_before)
        new_rec = ALDBRecord(rec.mem_addr, control_flags=new_flags, group=rec.group,
                             address=rec.address, data1=rec.data1, data2=rec.data2,
                             data3=rec.data3)
        self._dirty_records[new_rec.mem_addr] = new_rec

    def _get_next_mem_addr(self):
        """Return the next memory slot available."""
        if not self.is_loaded():
            return None

        last_record = None
        for record in self:
            last_record = record
            control_flags = record.control_flags
            if control_flags.is_high_water_mark or not control_flags.in_use:
                return record.mem_addr

        return last_record.mem_addr - 8

    def calc_load_status(self):
        """Test if the ALDB is fully loaded."""
        has_first = False
        has_last = False
        has_all = False
        last_addr = 0x0000
        first = True
        for mem_addr in sorted(self._records, reverse=True):
            if first:
                _LOGGER.debug('First Addr: 0x%4x', mem_addr)
            if mem_addr == self._mem_addr:
                has_first = True
            if self._records[mem_addr].control_flags.is_high_water_mark:
                has_last = True
            if last_addr != 0x0000:
                has_all = (last_addr - mem_addr) == 8
            last_addr = mem_addr
        _LOGGER.debug('Has First is %s', has_first)
        _LOGGER.debug('Has Last is %s', has_last)
        _LOGGER.debug('Has All is %s', has_all)
        return has_first and has_all and has_last

    def _set_load_status(self):
        _LOGGER.debug('Setting the load status')
        if self.calc_load_status():
            self._status = ALDBStatus.LOADED
        elif self._records:
            self._status = ALDBStatus.PARTIAL
        else:
            self._status = ALDBStatus.EMPTY


class ModemALDB(ALDBBase):
    """All-Link database for modems.

    Subscribed topics:
    modem.aldb.loaded: Triggered when the ALDB load command completes.

    Messages sent:
    modem.aldb.load: Triggers the loading of the ALDB.
    """

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0000):
        """Init the ModemALDB."""
        from ..managers.im_read_manager import ImReadManager
        super().__init__(address, version, mem_addr)
        self._read_manager = ImReadManager(self)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._records[mem_addr] = record

    async def async_load(self, callback: Callable = None):
        """Load the All-Link Database."""
        _LOGGER.debug('Loading the modem ALDB')
        self._records = {}
        await self._read_manager.async_load()
        self._status = ALDBStatus.LOADED
        if callback:
            callback()
        return self._status
