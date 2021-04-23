"""Insteon All-Link Database.

The All-Link database contains database records that represent links to other
Insteon devices that either respond to or control the current device.
"""
import asyncio
import logging
from typing import Callable

from ..constants import ALDBStatus, ALDBVersion
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
        self._update_status(ALDBStatus.LOADING)
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
        _LOGGER.debug("Checking ALDB load status: %s", self._address.id)
        for mem_addr in sorted(self._records, reverse=True):
            if first:
                _LOGGER.debug("First Addr: 0x%04x", mem_addr)
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

    def set_load_status(self):
        """Review the ALDB records and identify the load status."""
        _LOGGER.debug("Setting the load status")
        if self._calc_load_status():
            self._update_status(ALDBStatus.LOADED)
        elif self._records:
            self._update_status(ALDBStatus.PARTIAL)
        else:
            self._update_status(ALDBStatus.EMPTY)

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

    async def _async_write_change(self, record):
        """Write a changed record."""
        response = ResponseStatus.UNSENT
        retries = 0
        while response != ResponseStatus.SUCCESS and retries < 3:
            response = await self._write_manager.async_write(record)
            _LOGGER.debug("Response: %s", str(response))
            retries += 1
        return response == ResponseStatus.SUCCESS

    async def _async_write_delete(self, record):
        """Write a deleted record."""
        return await self._async_write_change(record)

    async def _async_write_new(self, record):
        """Write a new record."""
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
        return await self._async_write_change(record)
