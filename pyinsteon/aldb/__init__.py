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

    @property
    def is_loaded(self) -> bool:
        """Test if the ALDB is loaded."""
        return self._status == ALDBStatus.LOADED

    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return self._records.get(mem_addr, default)


class ALDB(ALDBBase):
    """All-Link Database for a device."""

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0fff):
        """Init the ALDB class."""
        from .read_manager import ALDBReadManager
        super().__init__(address=address, version=version, mem_addr=mem_addr)
        self._read_manager = ALDBReadManager(self)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._records[mem_addr] = record

        # After we add a record test load status
        if self._status == ALDBStatus.LOADING:
            return
        self._set_load_status()

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
        await self._read_manager.async_read(mem_addr=mem_addr, num_recs=num_recs)
        self._set_load_status()
        if callback:
            callback()
        return self._status

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
        from .im_read_manager import ImReadManager
        super().__init__(address, version, mem_addr)
        self._get_next_record_cmd: Callable
        self._read_manager = ImReadManager(self)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._records[mem_addr] = record

    def load(self, callback: Callable = None):
        """Load the All-Link Database."""
        asyncio.ensure_future(self.async_load(callback))

    async def async_load(self, callback: Callable = None):
        """Load the All-Link Database."""
        _LOGGER.debug('Loading the modem ALDB')
        self._records = {}
        await self._read_manager.async_load()
        self._status = ALDBStatus.LOADED
        if callback:
            callback()
        return self._status
