"""Insteon All-Link Database.

The All-Link database contains database records that represent links to other
Insteon devices that either respond to or control the current device.
"""

import asyncio
import logging
import time

from ..constants import ALDBStatus, EngineVersion, ReadWriteMode
from ..managers.aldb_read_manager import ALDBReadManager
from ..managers.device_health import get_health
from .aldb_base import HWM_RECORD, ALDBBase
from .aldb_record import new_aldb_record_from_existing

_LOGGER = logging.getLogger(__name__)

MAX_CONSECUTIVE_ERASED = 8


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
        self._top_mem_addr = mem_addr
        self._read_manager = ALDBReadManager(self._address, self._mem_addr)

    # pylint: disable=arguments-differ
    async def async_load(
        self, mem_addr: int = 0x00, num_recs: int = 0x00, refresh: bool = False
    ):
        """Load the All-Link Database."""
        waited = self._load_lock.locked()
        async with self._load_lock:
            # A background load that lands behind a finished one is redundant.
            # A refresh is not; the caller asked for a fresh read.
            if waited and not refresh and self._status == ALDBStatus.LOADED:
                return self._status
            previous_records = dict(self._records) if refresh else {}
            previous_status = self._status
            previous_mem_addr = self._mem_addr
            status = await self._async_load(
                mem_addr=mem_addr, num_recs=num_recs, refresh=refresh
            )
            # A refresh that dies partway must not replace the last good set
            if refresh and previous_records and status != ALDBStatus.LOADED:
                self.load_saved_records(
                    previous_status, previous_records, previous_mem_addr
                )
            return self._status

    async def _async_load(
        self, mem_addr: int = 0x00, num_recs: int = 0x00, refresh: bool = False
    ):
        """Load the All-Link Database without reentrancy protection."""
        health = get_health(self._address)
        if not refresh and not health.can_attempt_maintenance():
            _LOGGER.info(
                "Deferring ALDB load of %s: device unreachable, next attempt in %ds",
                self._address,
                max(0, int(health.next_maintenance - time.monotonic())),
            )
            return self._status
        _LOGGER.debug("Loading the ALDB async")
        self._update_status(ALDBStatus.LOADING)
        # Drop phantom records above the first record address. Erased 0xFF
        # cells from i3 devices were saved there by prior versions.
        self._mem_addr = min(self._mem_addr, self._top_mem_addr)
        for phantom_addr in [addr for addr in self._records if addr > self._mem_addr]:
            self._records.pop(phantom_addr)
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

        if self._mem_addr not in self._records:
            # Query the first record
            try:
                async for rec in self._read_manager.async_read(
                    mem_addr=0, num_recs=1, read_write_mode=mode
                ):
                    if rec.mem_addr <= self._top_mem_addr:
                        self._mem_addr = rec.mem_addr
                        self._add_record(rec)
            finally:
                await self._read_manager.async_stop()

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

        ended_in_erased_run = False
        if not self._is_loaded() and self._records:
            # Loading all records did not work so now we read individual missing
            # records. i3 devices erase deleted cells back to 0xFF rather than
            # clearing the in-use flag, so an erased cell mid-database is a
            # deleted slot. A single erased reply proves nothing, a garbled
            # response looks the same. Only a run of consecutive erased
            # cells ends the database; a silent cell just ends this attempt.
            consecutive_erased = 0
            next_record = self._calc_next_record()
            while next_record:
                got_record = False
                async for rec in self._read_manager.async_read(
                    mem_addr=next_record, num_recs=1
                ):
                    got_record = self._add_record(rec) or got_record
                if got_record:
                    consecutive_erased = 0
                elif self._read_manager.hit_erased:
                    consecutive_erased += 1
                    self._add_record(self._deleted_record(next_record))
                    if consecutive_erased >= MAX_CONSECUTIVE_ERASED:
                        ended_in_erased_run = True
                        break
                else:
                    # The ALDB did not return the requested record so stop
                    break
                next_record = self._calc_next_record()

        if ended_in_erased_run and not self._is_loaded():
            self._close_erased_aldb()

        if (
            not self._records
            and self._read_write_mode == ReadWriteMode.STANDARD
            and self._version == EngineVersion.I1
            and health.can_attempt_maintenance()
        ):
            # Peek reads are a last resort for confirmed i1 devices only. A
            # device that is simply not answering must not be walked one
            # byte at a time.
            self._read_write_mode = ReadWriteMode.PEEK_POKE
            return await self._async_load(
                mem_addr=mem_addr, num_recs=num_recs, refresh=refresh
            )

        self.set_load_status()
        if self._status == ALDBStatus.LOADED:
            get_health(self._address).record_success()

        return self._status

    def _deleted_record(self, mem_addr):
        """Return a record representing an erased (deleted) i3 cell."""
        return new_aldb_record_from_existing(
            HWM_RECORD, mem_addr=mem_addr, high_water_mark=False
        )

    def _close_erased_aldb(self):
        """Terminate a database that ends in erased 0xFF cells.

        i3 devices have no 0x00 high water mark record; the database ends at
        the first erased cell. Synthesize a high water mark there so the
        database can reach loaded status.
        """
        addrs = sorted(self._records, reverse=True)
        if not addrs or addrs[0] != self._mem_addr:
            return
        for first, second in zip(addrs, addrs[1:]):
            if first - second != 8:
                return
        hwm_addr = addrs[-1] - 8
        _LOGGER.debug("Synthesizing high water mark at 0x%04X", hwm_addr)
        self._add_record(new_aldb_record_from_existing(HWM_RECORD, mem_addr=hwm_addr))

    def _add_record(self, record) -> bool:
        """Add a record to the record set."""
        _LOGGER.debug("Loading record: %s", str(record))
        # Make sure the records make sense
        if record.mem_addr > self._mem_addr:
            _LOGGER.debug("Record is above the first record: %s", str(record))
            return False
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

        for mem_addr in range(self._mem_addr, last_addr - 8, -8):
            try:
                rec = self._records[mem_addr]
                if rec.is_high_water_mark:
                    return None
            except KeyError:
                return mem_addr

        return last_addr - 8
