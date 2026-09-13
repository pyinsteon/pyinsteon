"""Test how concurrent ALDB loads share or repeat the read."""

# pylint: disable=protected-access
import asyncio
import unittest

from pyinsteon.address import Address
from pyinsteon.aldb.aldb import ALDB
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ALDBStatus

from tests.utils import async_case, random_address


def _record(mem_addr, high_water_mark=False):
    return ALDBRecord(
        memory=mem_addr,
        controller=not high_water_mark,
        group=0 if high_water_mark else 1,
        target=Address("000000" if high_water_mark else "aabbcc"),
        data1=0,
        data2=0,
        data3=0,
        in_use=not high_water_mark,
        high_water_mark=high_water_mark,
    )


class GatedReadManager:
    """Serve a two record database, holding each bulk read until released."""

    def __init__(self):
        """Init the GatedReadManager class."""
        self.release = asyncio.Event()
        self.bulk_reads = 0
        self.hit_erased = False

    async def async_read(self, mem_addr=0x00, num_recs=0, read_write_mode=None):
        """Yield the records once released."""
        if mem_addr == 0x00 and num_recs == 0:
            self.bulk_reads += 1
            await self.release.wait()
            yield _record(0x0FFF)
            yield _record(0x0FF7, high_water_mark=True)
        elif mem_addr in (0x00, 0x0FFF):
            yield _record(0x0FFF)

    async def async_stop(self):
        """Stop the read."""


class TestConcurrentLoads(unittest.TestCase):
    """Test overlapping calls to async_load."""

    async def _run_overlapping(self, second_refresh):
        aldb = ALDB(Address("112233"))
        aldb._read_manager = GatedReadManager()
        first = asyncio.create_task(aldb.async_load())
        await asyncio.sleep(0.05)
        second = asyncio.create_task(aldb.async_load(refresh=second_refresh))
        await asyncio.sleep(0.05)
        aldb._read_manager.release.set()
        statuses = await asyncio.gather(first, second)
        return aldb, statuses

    @async_case
    async def test_background_load_shares_the_read_in_flight(self):
        """A second plain load waits for the first and reuses its result."""
        aldb, statuses = await self._run_overlapping(second_refresh=False)
        assert statuses == [ALDBStatus.LOADED, ALDBStatus.LOADED]
        assert aldb._read_manager.bulk_reads == 1

    @async_case
    async def test_refresh_is_not_swallowed_by_a_load_in_flight(self):
        """A refresh asked for during a load still reads the device."""
        aldb, statuses = await self._run_overlapping(second_refresh=True)
        assert statuses == [ALDBStatus.LOADED, ALDBStatus.LOADED]
        assert aldb._read_manager.bulk_reads == 2


class FailingReadManager:
    """Serve only the first record, then answer nothing."""

    def __init__(self):
        """Init the FailingReadManager class."""
        self.hit_erased = False

    async def async_read(self, mem_addr=0x00, num_recs=0, read_write_mode=None):
        """Yield the first record and nothing else."""
        if num_recs == 1 and mem_addr in (0x00, 0x0FFF):
            yield _record(0x0FFF)

    async def async_stop(self):
        """Stop the read."""


class ShrunkenReadManager:
    """Serve a database that is one record smaller than the cached one."""

    def __init__(self):
        """Init the ShrunkenReadManager class."""
        self.hit_erased = False

    async def async_read(self, mem_addr=0x00, num_recs=0, read_write_mode=None):
        """Yield a complete two record database."""
        if num_recs == 1 and mem_addr in (0x00, 0x0FFF):
            yield _record(0x0FFF)
        elif num_recs == 0:
            yield _record(0x0FFF)
            yield _record(0x0FF7, high_water_mark=True)

    async def async_stop(self):
        """Stop the read."""


class TestRefreshRollback(unittest.TestCase):
    """Test that a failed refresh does not destroy the cached records."""

    def _loaded_aldb(self, read_manager):
        aldb = ALDB(random_address())
        previous = {
            rec.mem_addr: rec
            for rec in [
                _record(0x0FFF),
                _record(0x0FF7),
                _record(0x0FEF, high_water_mark=True),
            ]
        }
        aldb.load_saved_records(ALDBStatus.LOADED, previous)
        aldb._read_manager = read_manager
        return aldb

    @async_case
    async def test_failed_refresh_restores_the_previous_records(self):
        """A refresh that dies partway leaves the last good record set."""
        aldb = self._loaded_aldb(FailingReadManager())
        status = await aldb.async_load(refresh=True)
        assert status == ALDBStatus.LOADED
        assert len(aldb) == 3
        assert aldb[0x0FF7] is not None

    @async_case
    async def test_complete_refresh_replaces_the_previous_records(self):
        """A refresh that reaches loaded keeps the fresh, smaller set."""
        aldb = self._loaded_aldb(ShrunkenReadManager())
        status = await aldb.async_load(refresh=True)
        assert status == ALDBStatus.LOADED
        assert len(aldb) == 2
        assert aldb.get(0x0FEF) is None


if __name__ == "__main__":
    unittest.main()
