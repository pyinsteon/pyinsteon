"""Insteon All-Link Database.

The All-Link database contains database records that represent links to other
Insteon devices that either respond to or control the current device.
"""
import asyncio
import logging
from typing import Callable

from ..address import Address
from ..constants import ALDBStatus, ALDBVersion
from .aldb_record import ALDBRecord
from .aldb_base import ALDBBase
from ..managers.aldb_read_manager import ALDBReadManager
from ..managers.aldb_write_manager import ALDBWriteManager
from ..handlers import ResponseStatus

_LOGGER = logging.getLogger(__name__)


class ALDB(ALDBBase):
    """All-Link Database for a device."""

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x0FFF):
        """Init the ALDB class."""

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
            self.clear()
        # pylint: disable=not-an-iterable
        async for rec in self._read_manager.async_read(
            mem_addr=mem_addr, num_recs=num_recs
        ):
            if self._hwm_record and rec.mem_addr < self._hwm_record.mem_addr:
                continue
            if rec.mem_addr > self.first_mem_addr:
                continue
            if self._records.get(rec.mem_addr):
                self._notify_change(self._records[rec.mem_addr], force_delete=True)
            self._records[rec.mem_addr] = rec
            if rec.is_high_water_mark:
                self._hwm_record = rec
            self._notify_change(rec)
        self.set_load_status()
        if callback:
            callback()
        return self._status

    def write(self, force=False):
        """Write modified records to the device."""
        asyncio.ensure_future(self.async_write(force=force))

    async def async_write(self, force=False):
        """Write modified records to the device.

        Returns a tuple of (completed, failed) record counts.
        """

        if not self.is_loaded and not force:
            _LOGGER.warning(
                "ALDB must be loaded before it can be written Status: %s",
                str(self._status),
            )
            return

        completed = []
        failed = []
        for record in self._dirty_records:
            if record.mem_addr == 0x0000:
                mem_addr = self._existing_link(
                    record.is_controller, record.group, record.target
                )
                if mem_addr is None:
                    _LOGGER.debug("Existing record not found")
                    mem_addr = self._get_next_mem_addr()
                    _LOGGER.debug("Using new record %04x", mem_addr)
                else:
                    _LOGGER.debug("Using existing record %04x", mem_addr)
                record.mem_addr = mem_addr
            # We assume a direct ACK is a confirmation of write.
            # Should we re-read to ensure it is correct.
            response = ResponseStatus.UNSENT
            retries = 0
            while response != ResponseStatus.SUCCESS and retries < 3:
                response = await self._write_manager.async_write(record)
                _LOGGER.debug("Response: %s", str(response))
                retries += 1
            if response == ResponseStatus.SUCCESS:
                self._records[record.mem_addr] = record
                completed.append(record)
            else:
                failed.append(record)
        self._dirty_records = failed
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
            if not record.is_in_use:
                _LOGGER.debug("Using the available record %04x", record.mem_addr)
                return record.mem_addr

        _LOGGER.debug("Using the next vailable record %04x", record.mem_addr)
        return last_record.mem_addr - 8

    def _calc_load_status(self):
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

    def set_load_status(self):
        """Review the ALDB records and identify the load status."""
        _LOGGER.debug("Setting the load status")
        if self._calc_load_status():
            self._status = ALDBStatus.LOADED
        elif self._records:
            self._status = ALDBStatus.PARTIAL
        else:
            self._status = ALDBStatus.EMPTY

    def _confirm_hwm(self, rec):
        """Confirm the new record is not below the High Wter Mark.

        The ALDB will often respond with records that are below the HWM.
        This method confirms no records below the HWM are added.
        If a new HWM is received, this will also remove records below it.

        Records below the HWM are never used by the device and are therefore
        irrelivant.
        """
        curr_hwm_mem_addr = 0x0000
        for curr_mem_addr in self._records:
            curr_rec = self._records[curr_mem_addr]
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
