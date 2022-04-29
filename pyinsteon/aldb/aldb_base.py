"""Base class for the All-Link Database."""

import logging
from abc import ABC, abstractmethod
from typing import List, Tuple

from ..address import Address
from ..constants import ALDBStatus, ALDBVersion, ResponseStatus
from ..managers.aldb_write_manager import ALDBWriteException, ALDBWriteManager
from ..topics import (
    ALDB_STATUS_CHANGED,
    ALDB_VERSION,
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_CONTROLLER_REMOVED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from ..utils import publish_topic, subscribe_topic
from .aldb_record import ALDBRecord, new_aldb_record_from_existing

_LOGGER = logging.getLogger(__name__)
HWM_RECORD = ALDBRecord(
    0x0000,
    controller=False,
    group=0,
    target="000000",
    data1=0,
    data2=0,
    data3=0,
    in_use=False,
    high_water_mark=True,
    bit4=False,
    bit5=False,
)


class ALDBBase(ABC):
    """Represents a base class for a device All-Link database."""

    def __init__(
        self,
        address,
        version=ALDBVersion.V2,
        mem_addr=0x0FFF,
        write_manager=ALDBWriteManager,
    ):
        """Instantiate the ALL-Link Database object."""
        self._records = {}
        self._status = ALDBStatus.EMPTY
        self._version = version

        self._address = Address(address)
        self._mem_addr = mem_addr
        self._read_manager = None
        self._write_manager = write_manager(self)
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
        return ", ".join(f"{k}: {repr(v)}" for k, v in attrs.items())

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
    def high_water_mark_mem_addr(self) -> int:
        """Return the High Water Mark record memory address."""
        for mem_addr, rec in self._records.items():
            if rec.is_high_water_mark:
                return mem_addr
        return None

    @property
    def is_loaded(self) -> bool:
        """Test if the ALDB is loaded."""
        if self._status == ALDBStatus.LOADING:
            loaded = self._calc_load_status()
            if loaded:
                self._update_status(ALDBStatus.LOADED)
        return self._status == ALDBStatus.LOADED

    @property
    def pending_changes(self):
        """Return pending changes."""
        return self._dirty_records

    def clear(self):
        """Clear all records from the ALDB.

        This does not write to the device.
        """
        for _, rec in self._records.items():
            self._notify_change(rec, force_delete=True)
        self._records = {}
        self._dirty_records = {}

    def clear_pending(self):
        """Remove pending changes."""
        self._dirty_records = {}

    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return self._records.get(mem_addr, default)

    def get_responders(self, group):
        """Return an iterable of responders to this device for a group.

        Note this only returns the responders known to this device.
        There may be other responders since a device may have
        a `responder` record that is not in the `controller`
        All-Link Database.
        """
        for _, rec in self._records.items():
            if rec.is_controller and rec.group == group:
                yield rec.target

    def update_version(self, version: ALDBVersion):
        """Update the ALDB version number."""
        self._version = ALDBVersion(version)

    def subscribe_status_changed(self, listener):
        """Subscribe to notification of ALDB load status changes."""
        subscribe_topic(listener, f"{self._address.id}.{ALDB_STATUS_CHANGED}")

    def subscribe_record_changed(self, listener):
        """Subscribe to notification of ALDB record changes."""
        subscribe_topic(
            listener, f"{DEVICE_LINK_CONTROLLER_CREATED}.{self._address.id}"
        )
        subscribe_topic(
            listener, f"{DEVICE_LINK_CONTROLLER_REMOVED}.{self._address.id}"
        )
        subscribe_topic(listener, f"{DEVICE_LINK_RESPONDER_CREATED}.{self._address.id}")
        subscribe_topic(listener, f"{DEVICE_LINK_RESPONDER_REMOVED}.{self._address.id}")

    @abstractmethod
    async def async_load(self, *args, **kwargs):
        """Load the All-Link Database."""
        raise NotImplementedError

    def load_saved_records(
        self, status: ALDBStatus, records: List[ALDBRecord], first_mem_addr: int = None
    ):
        """Load All-Link records from a dictionary of saved records."""
        self._update_status(status)
        self.clear()
        for mem_addr in records:
            record = records[mem_addr]
            self._records[mem_addr] = record
            self._notify_change(record)
        if self.is_loaded and self._records:
            self._mem_addr = max(self._records)
        if first_mem_addr is not None:
            self._mem_addr = first_mem_addr

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
        new_rec = ALDBRecord(
            memory=0x0000,
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

        for curr_rec in self.find(
            target=new_rec.target,
            is_controller=new_rec.is_controller,
            group=new_rec.group,
        ):
            new_rec.mem_addr = curr_rec.mem_addr
            break

        if new_rec.mem_addr == 0x0000:
            mem_addr = self._next_new_mem_addr()
        else:
            mem_addr = new_rec.mem_addr

        self._dirty_records[mem_addr] = new_rec

    def remove(self, mem_addr: int):
        """Remove an All-Link record."""
        rec = self._records.get(mem_addr)
        if not rec:
            raise IndexError("Memory location not found.")

        new_rec = new_aldb_record_from_existing(rec, in_use=False)
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

        new_rec = new_aldb_record_from_existing(
            rec,
            in_use=in_use,
            controller=controller,
            high_water_mark=high_water_mark,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            bit5=bit5,
            bit4=bit4,
        )
        self._dirty_records[mem_addr] = new_rec

    async def async_write(self, force=False) -> Tuple[int, int]:
        """Write the dirty records to the device."""
        if not self.is_loaded and not force:
            _LOGGER.warning(
                "ALDB must be loaded before it can be written Status: %s",
                str(self._status),
            )
            return 0, len(self._dirty_records)
        success = 0
        failed = {}
        dirty_addrs = sorted(self._dirty_records, reverse=True)
        next_new_dirty = 0
        for dirty_addr in dirty_addrs:
            try:
                rec = self._dirty_records.pop(dirty_addr)
            except KeyError:
                pass
            rec_to_write = rec.copy()
            if rec.mem_addr == 0x000:
                rec_to_write.mem_addr = self._next_record_mem_addr(
                    target=rec.target,
                    group=rec.group,
                    is_controller=rec.is_controller,
                    force=force,
                )
            result = False
            try:
                result = await self._write_manager.async_write(rec_to_write, force)
            except ALDBWriteException:
                result = ResponseStatus.FAILURE

            if result == ResponseStatus.SUCCESS:
                curr_rec = self._records.get(rec_to_write.mem_addr)
                # If we wrote to the high water mark, append a new HWM record
                if curr_rec and curr_rec.is_high_water_mark:
                    new_hwm_rec = new_aldb_record_from_existing(
                        HWM_RECORD, mem_addr=curr_rec.mem_addr - 8
                    )
                    self._records[new_hwm_rec.mem_addr] = new_hwm_rec
                self._records[rec_to_write.mem_addr] = rec_to_write
                success += 1
                self._notify_change(rec_to_write)
            else:
                if rec.mem_addr == 0x0000:
                    next_new_dirty -= 1
                    failed[next_new_dirty] = rec
                else:
                    failed[rec.mem_addr] = rec

        self._dirty_records = failed
        return success, len(self._dirty_records)

    def find(
        self,
        group: int = None,
        target: Address = None,
        is_controller: bool = None,
        in_use: bool = None,
    ) -> List[ALDBRecord]:
        """Find all records matching the criteria."""
        if (
            group is None
            and target is None
            and is_controller is None
            and in_use is None
        ):
            raise ValueError("Must have at least one criteria")

        for _, rec in self._records.items():
            group_match = group is None or rec.group == group
            target_match = target is None or rec.target == target
            is_controller_match = (
                is_controller is None or rec.is_controller == is_controller
            )
            in_use_match = in_use is None or rec.is_in_use == in_use
            if group_match and target_match and is_controller_match and in_use_match:
                yield rec

    def set_load_status(self):
        """Review the ALDB records and identify the load status."""
        _LOGGER.debug("Setting the load status")
        if self._calc_load_status():
            self._update_status(ALDBStatus.LOADED)
        elif self._records:
            self._update_status(ALDBStatus.PARTIAL)
        else:
            self._update_status(ALDBStatus.EMPTY)

    def _update_status(self, status):
        """Update the status of the ALDB and notify listeners."""
        new_status = ALDBStatus(int(status))
        if new_status != self._status:
            self._status = new_status
            publish_topic(f"{self._address.id}.{ALDB_STATUS_CHANGED}")

    def _notify_change(self, record, force_delete=False):
        target = record.target
        group = record.group
        is_in_use = True if force_delete else record.is_in_use
        if record.is_controller and is_in_use:
            topic = f"{DEVICE_LINK_CONTROLLER_CREATED}.{self._address.id}"
            controller = self._address
            responder = target
        elif record.is_controller and not is_in_use:
            topic = f"{DEVICE_LINK_CONTROLLER_REMOVED}.{self._address.id}"
            controller = self._address
            responder = target
        elif not record.is_controller and is_in_use:
            topic = f"{DEVICE_LINK_RESPONDER_CREATED}.{self._address.id}"
            controller = target
            responder = self._address
        else:
            topic = f"{DEVICE_LINK_RESPONDER_REMOVED}.{self._address.id}"
            controller = target
            responder = self._address

        publish_topic(topic, controller=controller, responder=responder, group=group)

    def _next_new_mem_addr(self):
        """Return the next temporary memory address to use for a new record.

        This is a temporary address assigned to a new record until the time
        of writing. When `async_write` is called, an actual address will be
        assigned.
        """
        if not self._dirty_records:
            return -1
        return min(min(self._dirty_records), 0) - 1

    def _next_record_mem_addr(
        self, target: Address, group: int, is_controller: bool, force: bool = False
    ):
        """Assign a memory address to a record.

        Looks for an existing memory address with the same:
        1. Target
        2. Group
        3. Link mode (ie. controller / responder)

        If it finds an existing record with the same values, it overwrites the original rather than
        creating a new record. This ensures there is only one record with the same target, group and link mode.

        If it cannot find an existing record than it returns the next unused record.

        If the ALDB is not loaded it returns an ALDBWriteException
        """
        if not self.is_loaded and not force:
            raise ALDBWriteException("Cannot calculate the next record to write to.")

        for existing_record in self.find(
            target=target, group=group, is_controller=is_controller
        ):
            return existing_record.mem_addr

        next_mem_addr = self._mem_addr
        for mem_addr, rec in self._records.items():
            if not rec.is_in_use or rec.is_high_water_mark:
                # This should always be the return if the ALDB is loaded
                return mem_addr
            if mem_addr != next_mem_addr:
                return next_mem_addr
            next_mem_addr = mem_addr - 8
        if not force:
            raise ALDBWriteException(
                "An unknown error in finding the next ALDB record memory address."
            )
        return next_mem_addr

    def _calc_load_status(self):
        """Test if the ALDB is fully loaded."""
        has_first = False
        has_last = False
        has_all = False
        last_addr = 0x0000
        for mem_addr in sorted(self._records, reverse=True):
            if mem_addr == self._mem_addr:
                has_first = True
            if self._records[mem_addr].is_high_water_mark:
                has_last = True
            if last_addr != 0x0000:
                has_all = (last_addr - mem_addr) == 8
            if len(self._records) == 1 and has_last and has_first:
                # Empty ALDB; yes it is possible with some devices like motion
                has_all = True
            last_addr = mem_addr
        _LOGGER.debug("Has First is %s", has_first)
        _LOGGER.debug("Has Last is %s", has_last)
        _LOGGER.debug("Has All is %s", has_all)
        return has_first and has_all and has_last

    def _confirm_hwm(self, rec):
        """Confirm the new record is not below the High Water Mark.

        The ALDB will often respond with records that are below the HWM.
        This method confirms no records below the HWM are added.
        If a new HWM is received, this will also remove records below it.

        Records below the HWM are never used by the device and are therefore
        irrelivant.
        """
        curr_hwm_mem_addr = 0x0000
        for curr_mem_addr, curr_rec in self._records.items():
            if curr_rec.is_high_water_mark:
                curr_hwm_mem_addr = curr_mem_addr
                break

        found_hwm = (
            curr_hwm_mem_addr != 0x0000
            and self._records[curr_hwm_mem_addr].is_high_water_mark
        )

        if rec.is_high_water_mark and rec.mem_addr < curr_hwm_mem_addr:
            curr_hwm_mem_addr = rec.mem_addr

        elif found_hwm and rec.is_high_water_mark and rec.mem_addr > curr_hwm_mem_addr:
            return False

        remove_records = []
        for curr_mem_addr in self._records:
            if found_hwm and curr_mem_addr < curr_hwm_mem_addr:
                remove_records.append(curr_mem_addr)

        for mem_addr in remove_records:
            self._records.pop(mem_addr)

        return True
