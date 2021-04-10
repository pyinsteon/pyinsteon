"""Base class for the All-Link Database."""
import asyncio
import logging
from abc import ABC, abstractmethod

from ..utils import publish_topic, subscribe_topic
from ..address import Address
from ..constants import ALDBStatus, ALDBVersion
from ..topics import (
    ALDB_VERSION,
    ALDB_STATUS_CHANGED,
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_CONTROLLER_REMOVED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from .aldb_record import ALDBRecord

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
        self._dirty_records = {}
        self._hwm_record = None
        subscribe_topic(self.update_version, f"{repr(self._address)}.{ALDB_VERSION}")

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

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError
        if mem_addr == 0:
            mem_addr = self._next_new_mem_addr()
            record.mem_addr = 0
        else:
            record.mem_addr = mem_addr
        self._dirty_records[mem_addr] = record

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ", ".join("%s: %r" % item for item in attrs.items())

    @property
    def address(self) -> Address:
        """Return the address of the device."""
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
        if self._hwm_record:
            return self._hwm_record.mem_addr
        return None

    @property
    def is_loaded(self) -> bool:
        """Test if the ALDB is loaded."""
        if self._status == ALDBStatus.LOADING:
            loaded = self._calc_load_status()
            if loaded:
                self._update_status(ALDBStatus.LOADED)
        return self._status == ALDBStatus.LOADED

    def clear(self):
        """Clear all records from the ALDB.

        This does not write to the device.
        """
        for mem in self._records:
            rec = self._records[mem]
            self._notify_change(rec, force_delete=True)
        self._records = {}
        self._dirty_records = {}

    @property
    def pending_changes(self):
        """Return pending changes."""
        return self._dirty_records

    def clear_pending(self):
        """Remove pending changes."""
        self._dirty_records = {}

    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return self._records.get(mem_addr, default)

    def get_responders(self, group):
        """Return all responders to this device for a group."""
        for mem_addr in self._records:
            rec = self._records[mem_addr]
            if rec.is_controller and rec.group == group:
                yield rec.target

    def update_version(self, version):
        """Update the ALDB version number."""
        self._version = version

    def _update_status(self, status):
        """Update the status of the ALDB and notify listeners."""
        self._status = ALDBStatus(int(status))
        publish_topic(f"{self._address.id}.{ALDB_STATUS_CHANGED}")

    @abstractmethod
    async def async_load(self, *args, **kwargs):
        """Load the All-Link Database."""

    def load_saved_records(self, status: ALDBStatus, records: [ALDBRecord]):
        """Load All-Link records from a dictionary of saved records."""
        self._update_status(status)
        self.clear()
        for mem_addr in records:
            record = records[mem_addr]
            self._records[mem_addr] = record
            self._notify_change(record)
        if self.is_loaded and self._records:
            keys = list(self._records.keys())
            keys.sort(reverse=True)
            self._mem_addr = keys[0]

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

        new_rec = ALDBRecord(
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
        self._dirty_records[self._next_new_mem_addr()] = new_rec

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
        self._dirty_records[mem_addr] = new_rec

    def modify(
        self,
        mem_addr: int,
        in_use: bool = None,
        group: int = None,
        controller: bool = None,
        high_water_mark: bool = None,
        target: Address = None,
        data1: int = None,
        data2: int = None,
        data3: int = None,
        bit5: bool = None,
        bit4: bool = None,
    ):
        """Modify an All-Link record."""
        rec = self._records.get(mem_addr)
        if not rec:
            raise IndexError("Memory location not found.")

        new_in_use = rec.in_use if in_use is None else bool(in_use)
        new_group = rec.group if group is None else int(group)
        new_controller = rec.is_controller if controller is None else bool(controller)
        new_high_water_mark = (
            rec.is_high_water_mark if high_water_mark is None else bool(high_water_mark)
        )
        new_target = rec.target if target is None else Address(target)
        new_data1 = rec.data1 if data1 is None else data1
        new_data2 = rec.data2 if data2 is None else data2
        new_data3 = rec.data3 if data3 is None else data3
        new_bit5_set = rec.is_bit5_set if bit5 is None else bool(bit5)
        new_bit4_set = rec.is_bit4_set if bit4 is None else bool(bit4)
        new_rec = ALDBRecord(
            memory=rec.mem_addr,
            in_use=new_in_use,
            controller=new_controller,
            high_water_mark=new_high_water_mark,
            group=new_group,
            target=new_target,
            data1=new_data1,
            data2=new_data2,
            data3=new_data3,
            bit5=new_bit5_set,
            bit4=new_bit4_set,
        )
        self._dirty_records[mem_addr] = new_rec

    def write(self, force=False):
        """Write modified records to the device."""
        asyncio.ensure_future(self.async_write(force=force))

    async def async_write(self, force=False):
        """Write the dirty records to the device."""
        if not self.is_loaded and not force:
            _LOGGER.warning(
                "ALDB must be loaded before it can be written Status: %s",
                str(self._status),
            )
            return 0, 0
        success = 0
        failed = []
        for mem_addr in self._dirty_records:
            result = False
            rec = self._dirty_records[mem_addr]
            if mem_addr < 0:
                result = await self._async_write_new(rec)
            elif not rec.is_in_use:
                result = await self._async_write_delete(rec)
            else:
                result = await self._async_write_change(rec)
            if result:
                success += 1
            else:
                failed.append(rec)
        self._dirty_records = {rec.mem_addr: rec for rec in failed}
        return success, len(self._dirty_records)

    def _notify_change(self, record, force_delete=False):
        target = record.target
        group = record.group
        is_in_use = True if force_delete else record.is_in_use
        if record.is_controller and is_in_use:
            topic = f"{DEVICE_LINK_CONTROLLER_CREATED}.{self._address.id}"
        elif record.is_controller and not is_in_use:
            topic = f"{DEVICE_LINK_CONTROLLER_REMOVED}.{self._address.id}"
        elif not record.is_controller and is_in_use:
            topic = f"{DEVICE_LINK_RESPONDER_CREATED}.{self._address.id}"
        else:
            topic = f"{DEVICE_LINK_RESPONDER_REMOVED}.{self._address.id}"

        self._send_change(topic, self._address, target, group)

    @classmethod
    def _send_change(cls, topic, controller, responder, group):
        publish_topic(topic, controller=controller, responder=responder, group=group)

    # pylint: disable=no-self-use
    def _calc_load_status(self):
        """Calculate the load status."""
        return False

    def _next_new_mem_addr(self):
        """Return the next memory address to use for a new record."""
        if not self._dirty_records:
            return -1
        return min(min(self._dirty_records.keys()), 0) - 1

    @abstractmethod
    async def _async_write_new(self, record):
        """Write a new record."""

    @abstractmethod
    async def _async_write_delete(self, record):
        """Write a deleted record."""

    @abstractmethod
    async def _async_write_change(self, record):
        """Write a changed record."""
