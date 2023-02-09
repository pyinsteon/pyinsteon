"""Insteon All-Link Database.

The All-Link database contains database records that represent links to other
Insteon devices that either respond to or control the current device.
"""
import asyncio
import logging

from ..constants import ALDBStatus, EngineVersion, ReadWriteMode
from ..managers.aldb_read_manager import ALDBReadManager
from .aldb_base import ALDBBase

_LOGGER = logging.getLogger(__name__)


class ALDB(ALDBBase):
    """All-Link Database for a device."""

    def __init__(
        self,
        address,
        version=EngineVersion.UNKNOWN,
        mem_addr=0x0FFF,
    ):
        """Init the ALDB class."""
        super().__init__(address=address, version=version, mem_addr=mem_addr)
        self._read_manager = ALDBReadManager(self._address, self._mem_addr)

    # pylint: disable=arguments-differ
    async def async_load(
        self, mem_addr: int = 0x00, num_recs: int = 0x00, refresh: bool = False
    ):
        """Load the All-Link Database."""
        _LOGGER.debug("Loading the ALDB async")
        self._update_status(ALDBStatus.LOADING)
        if refresh:
            self.clear()
        else:
            # Pop any unused records to make sure we query them
            unused = list(self.find(in_use=False))
            for rec in unused:
                self._records.pop(rec.mem_addr)

        if self._read_write_mode == ReadWriteMode.UNKNOWN:
            mode = ReadWriteMode.STANDARD
        else:
            mode = self._read_write_mode
        try:
            async for rec in self._read_manager.async_read(
                mem_addr=mem_addr,
                num_recs=num_recs,
                read_write_mode=mode,
            ):
                self._add_record(rec)
                await asyncio.sleep(0.1)
                if self._read_write_mode == ReadWriteMode.UNKNOWN:
                    self._read_write_mode = mode
                if self._is_loaded():
                    break
        finally:
            await self._read_manager.async_stop()

        if not self._is_loaded() and num_recs != 0:
            # Loading all records did not work so now we read individual missing records
            next_record = self._calc_next_record()
            while next_record:
                async for rec in self._read_manager.async_read(
                    mem_addr=next_record, num_recs=1
                ):
                    self._add_record(rec)
                prev_record = next_record
                next_record = self._calc_next_record()
                if next_record == prev_record:
                    # The ALDB did not return the requested record so stop
                    break

        if (
            not self._records
            and self._read_write_mode == ReadWriteMode.STANDARD
            and self._version not in [EngineVersion.I2CS, EngineVersion.OTHER]
        ):
            self._read_write_mode = ReadWriteMode.PEEK_POKE
            return self.async_load(
                mem_addr=mem_addr, num_recs=num_recs, refresh=refresh
            )

        self.set_load_status()

        return self._status

    def _add_record(self, record) -> bool:
        """Add a record to the record set."""
        _LOGGER.debug("Loading record: %s", str(record))
        # Make sure the records make sense
        if (
            self.high_water_mark_mem_addr
            and record.mem_addr < self.high_water_mark_mem_addr
        ):
            _LOGGER.debug("Record is after the HWM: %s", str(record))
            return False

        # If an existing record will be replaced notify of change
        old_record = self._records.get(record.mem_addr)

        # If the old rec is identical to the new rec, do nothing
        if old_record and record.is_exact_match(old_record):
            _LOGGER.debug("Record has not changed:")
            _LOGGER.debug("Old: %s", str(old_record))
            _LOGGER.debug("New: %s", str(record))
            return False

        if old_record and old_record.is_in_use:
            self._notify_change(self._records[record.mem_addr], force_delete=True)

        self._records[record.mem_addr] = record
        self._notify_change(record)
        return True

    def _calc_next_record(self) -> int:
        """Calculate the memory address of the next missing record."""
        if not self._records:
            return self._mem_addr
        last_addr = list(self)[-1]
        if last_addr == self._mem_addr:
            return last_addr - 8

        for mem_addr in range(self._mem_addr, last_addr, -8):
            try:
                rec = self._records[mem_addr]
                if mem_addr == last_addr and rec.is_high_water_mark:
                    return None
            except IndexError:
                return mem_addr

        return last_addr - 8
