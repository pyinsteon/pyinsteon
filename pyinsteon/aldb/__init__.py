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
from ..topics import (
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_CONTROLLER_REMOVED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from .. import pub


_LOGGER = logging.getLogger(__name__)


class ALDBBase(ABC):
    """Represents a base class for a device All-Link database."""

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x0FFF):
        """Instantiate the ALL-Link Database object."""
        self._records = {}
        self._status = ALDBStatus.EMPTY
        self._version = version

        self._address = Address(address)
        self._mem_addr = mem_addr
        self._cb_aldb_loaded = None
        self._read_manager = None
        self._dirty_records = []

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
        return ", ".join("%s: %r" % item for item in attrs.items())

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
    def high_water_mark_mem_addr(self):
        """Return the High Water Mark record memory address."""
        for mem_addr in self._records:
            record = self._records[mem_addr]
            if record.is_high_water_mark:
                return record.mem_addr
        return None

    @property
    def is_loaded(self) -> bool:
        """Test if the ALDB is loaded."""
        return self._status == ALDBStatus.LOADED

    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return self._records.get(mem_addr, default)

    def get_responders(self, group):
        """Return all responders to this device for a group."""
        for mem_addr in self._records:
            rec = self._records[mem_addr]
            if rec.is_controller and rec.group == group:
                yield rec.target

    @abstractmethod
    async def async_load(self, *args, **kwargs):
        """Load the All-Link Database."""

    def load_saved_records(self, status: ALDBStatus, records: [ALDBRecord]):
        """Load All-Link records from a dictionary of saved records."""
        if isinstance(status, ALDBStatus):
            self._status = status
        else:
            self._status = ALDBStatus(status)
        for mem_addr in records:
            record = records[mem_addr]
            self._notify_change(record, force_delete=True)
            self._records[mem_addr] = record
            self._notify_change(record)
        if self.is_loaded and self._records:
            keys = list(self._records.keys())
            keys.sort(reverse=True)
            self._mem_addr = keys[0]

    def _notify_change(self, record, force_delete=False):
        from .. import devices

        target = record.target
        group = record.group
        is_in_use = True if force_delete else record.is_in_use
        if group == 0 or target == devices.modem.address:
            return
        if record.is_controller and is_in_use:
            self._send_change(
                DEVICE_LINK_CONTROLLER_CREATED, self._address, target, group
            )
        elif record.is_controller and not is_in_use:
            self._send_change(
                DEVICE_LINK_CONTROLLER_REMOVED, self._address, target, group
            )
        elif not record.is_controller and is_in_use:
            self._send_change(
                DEVICE_LINK_RESPONDER_CREATED, self._address, target, group
            )
        else:
            self._send_change(
                DEVICE_LINK_RESPONDER_REMOVED, self._address, target, group
            )

    @classmethod
    def _send_change(cls, topic, controller, responder, group):
        pub.sendMessage(topic, controller=controller, responder=responder, group=group)


class ALDB(ALDBBase):
    """All-Link Database for a device."""

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x0FFF):
        """Init the ALDB class."""
        from ..managers.aldb_read_manager import ALDBReadManager
        from ..managers.aldb_write_manager import ALDBWriteManager

        super().__init__(address=address, version=version, mem_addr=mem_addr)
        self._read_manager = ALDBReadManager(self)
        self._write_manager = ALDBWriteManager(self)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._dirty_records.append(record)

    def load(self, refresh=False, callback: Callable = None):
        """Load the ALDB calling the callback when done."""
        self._cb_aldb_loaded = callback
        asyncio.ensure_future(self.async_load(refresh))

    # pylint: disable=arguments-differ
    async def async_load(
        self,
        mem_addr: int = 0x00,
        num_recs: int = 0x00,
        refresh: bool = False,
        callback: Callable = None,
    ):
        """Load the All-Link Database."""
        _LOGGER.debug("Loading the ALDB async")
        self._status = ALDBStatus.LOADING
        if refresh:
            for maddr in self._records:
                self._notify_change(self._records[maddr], force_delete=True)
            self._records = {}
        async for rec in self._read_manager.async_read(
            mem_addr=mem_addr, num_recs=num_recs
        ):
            if self._records.get(rec.mem_addr):
                self._notify_change(self._records[rec.mem_addr], force_delete=True)
            self._records[rec.mem_addr] = rec
            self._notify_change(rec)
        self._set_load_status()
        if callback:
            callback()
        return self._status

    def write(self):
        """Write modified records to the device."""
        if self.is_loaded:
            asyncio.ensure_future(self.async_write())

    async def async_write(self):
        """Write modified records to the device.

        Returns a tuple of (completed, failed) record counts.
        """
        from ..handlers import ResponseStatus

        completed = []
        failed = []
        while self._dirty_records:
            record = self._dirty_records.pop()
            if record.mem_addr == 0x0000:
                mem_addr = self._existing_link(
                    record.is_controller, record.group, record.target
                )
                if mem_addr is None:
                    mem_addr = self._get_next_mem_addr()
                record.mem_addr = mem_addr
            # We assume a direct ACK is a confirmation of write.
            # Should we re-read to ensure it is correct.
            response = ResponseStatus.UNSENT
            retries = 0
            while response != ResponseStatus.SUCCESS and retries < 3:
                response = await self._write_manager.async_write(record)
                retries += 1
            if response == ResponseStatus.SUCCESS:
                completed.append(record)
            else:
                failed.append(record)
        for record in failed:
            self._dirty_records.append(record)
        return len(completed), len(self._dirty_records)

    def add(
        self,
        group: int,
        target: Address,
        controller: bool = False,
        data1: int = 0x00,
        data2: int = 0x00,
        data3: int = 0x00,
        bit5: int = True,
        bit4: int = False,
    ):
        """Add an All-Link record.

        This method does not write to the device. To write modifications to the device
        use `write` or `async_write`.
        """
        mem_addr = 0x0000

        rec = ALDBRecord(
            memory=mem_addr,
            in_use=True,
            controller=controller,
            high_water_mark=False,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            bit5=bit5,
            bit4=bit4,
        )
        self._dirty_records.append(rec)

    def remove(self, mem_addr: int):
        """Remove an All-Link record."""
        rec = self._records.get(mem_addr)
        if not rec:
            raise IndexError("Memory location not found.")
        new_rec = ALDBRecord(
            memory=rec.mem_addr,
            in_use=False,
            controller=rec.is_controller,
            high_water_mark=rec.is_high_water_mark,
            group=rec.group,
            target=rec.target,
            data1=rec.data1,
            data2=rec.data2,
            data3=rec.data3,
            bit5=rec.is_bit5_set,
            bit4=rec.is_bit4_set,
        )
        self._dirty_records.append(new_rec)

    def _existing_link(self, is_controller, group, address):
        """Test if a link exists in a device ALDB."""
        for mem_addr in self._records:
            rec = self._records[mem_addr]
            if (
                rec.is_controller == is_controller
                and rec.target == address
                and rec.group == group
            ):
                return rec.mem_addr
        return None

    def _get_next_mem_addr(self):
        """Return the next memory slot available."""
        if not self.is_loaded:
            return None

        last_record = None
        for mem_addr in self._records:
            record = self._records[mem_addr]
            last_record = record
            if record.is_high_water_mark or not record.is_in_use:
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
                _LOGGER.debug("First Addr: 0x%4x", mem_addr)
            if mem_addr == self._mem_addr:
                has_first = True
            if self._records[mem_addr].is_high_water_mark:
                has_last = True
            if last_addr != 0x0000:
                has_all = (last_addr - mem_addr) == 8
            last_addr = mem_addr
        _LOGGER.debug("Has First is %s", has_first)
        _LOGGER.debug("Has Last is %s", has_last)
        _LOGGER.debug("Has All is %s", has_all)
        return has_first and has_all and has_last

    def _set_load_status(self):
        _LOGGER.debug("Setting the load status")
        if self.calc_load_status():
            self._status = ALDBStatus.LOADED
        elif self._records:
            self._status = ALDBStatus.PARTIAL
        else:
            self._status = ALDBStatus.EMPTY
