"""Test handling of i3 erased (0xFF) ALDB cells."""

# pylint: disable=protected-access
import unittest

from pyinsteon.address import Address
from pyinsteon.aldb.aldb import ALDB, MAX_CONSECUTIVE_ERASED
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ALDBStatus
from pyinsteon.managers.aldb_read_manager import is_erased_record

from tests.utils import async_case


def _erased_record(mem_addr):
    return ALDBRecord(
        memory=mem_addr,
        controller=True,
        group=0xFF,
        target=Address("FFFFFF"),
        data1=0xFF,
        data2=0xFF,
        data3=0xFF,
        in_use=True,
        high_water_mark=False,
        bit5=True,
        bit4=True,
    )


def _real_record(mem_addr, group=1, controller=True):
    return ALDBRecord(
        memory=mem_addr,
        controller=controller,
        group=group,
        target=Address("aabbcc"),
        data1=3,
        data2=28,
        data3=1,
        in_use=True,
        high_water_mark=False,
    )


class TestErasedRecordDetection(unittest.TestCase):
    """Test is_erased_record."""

    def test_detects_erased_cell(self):
        """An all 0xFF record is erased."""
        assert is_erased_record(_erased_record(0xFFFC))

    def test_real_record_not_erased(self):
        """A real link record is not erased."""
        assert not is_erased_record(_real_record(0x0FFF))

    def test_hwm_not_erased(self):
        """A 0x00 high water mark record is not erased."""
        hwm = ALDBRecord(
            memory=0x0FBF,
            controller=False,
            group=0,
            target=Address("000000"),
            data1=0,
            data2=0,
            data3=0,
            in_use=False,
            high_water_mark=True,
        )
        assert not is_erased_record(hwm)


class TestErasedAldbHandling(unittest.TestCase):
    """Test ALDB behavior around erased cells and phantoms."""

    @async_case
    async def test_add_record_rejects_phantom_above_first(self):
        """Records above the first record address are rejected."""
        aldb = ALDB(Address("112233"))
        assert not aldb._add_record(_erased_record(0xFFFC))
        assert 0xFFFC not in aldb

    @async_case
    async def test_calc_next_record_returns_missing(self):
        """The first missing address in the chain is returned."""
        aldb = ALDB(Address("112233"))
        aldb._add_record(_real_record(0x0FFF))
        aldb._add_record(_real_record(0x0FEF))
        assert aldb._calc_next_record() == 0x0FF7

    @async_case
    async def test_calc_next_record_stops_at_hwm(self):
        """No further reads once a high water mark exists."""
        aldb = ALDB(Address("112233"))
        aldb._add_record(_real_record(0x0FFF))
        aldb._add_record(
            ALDBRecord(
                memory=0x0FF7,
                controller=False,
                group=0,
                target=Address("000000"),
                data1=0,
                data2=0,
                data3=0,
                in_use=False,
                high_water_mark=True,
            )
        )
        assert aldb._calc_next_record() is None

    @async_case
    async def test_close_erased_aldb_synthesizes_hwm(self):
        """A contiguous chain ending in erased cells becomes loaded."""
        aldb = ALDB(Address("112233"))
        aldb._add_record(_real_record(0x0FFF))
        aldb._add_record(_real_record(0x0FF7, group=1, controller=False))
        assert not aldb._is_loaded()
        aldb._close_erased_aldb()
        assert aldb.high_water_mark_mem_addr == 0x0FEF
        assert aldb._is_loaded()
        aldb.set_load_status()
        assert aldb.status == ALDBStatus.LOADED

    @async_case
    async def test_close_erased_aldb_requires_contiguous_chain(self):
        """A gap in the chain prevents synthesizing a high water mark."""
        aldb = ALDB(Address("112233"))
        aldb._add_record(_real_record(0x0FFF))
        aldb._add_record(_real_record(0x0FEF))
        aldb._close_erased_aldb()
        assert aldb.high_water_mark_mem_addr is None
        assert not aldb._is_loaded()


def _hwm_record(mem_addr):
    return ALDBRecord(
        memory=mem_addr,
        controller=False,
        group=0,
        target=Address("000000"),
        data1=0,
        data2=0,
        data3=0,
        in_use=False,
        high_water_mark=True,
    )


ERASED = "erased"


class ScriptedReadManager:
    """Serve a scripted device memory map in place of the real read manager.

    Each address maps to a record, ERASED for a cell that comes back as
    0xFF bytes, or None for a cell the device never answers for.
    """

    def __init__(self, memory, top=0x0FFF):
        """Init the ScriptedReadManager class."""
        self.memory = memory
        self.top = top
        self.hit_erased = False
        self.requests = []

    async def async_read(self, mem_addr=0x00, num_recs=0, read_write_mode=None):
        """Yield the scripted records for a read request."""
        self.hit_erased = False
        self.requests.append((mem_addr, num_recs))
        if mem_addr == 0x00 and num_recs == 0:
            for addr in sorted(self.memory, reverse=True):
                cell = self.memory[addr]
                if cell is None:
                    return
                if cell == ERASED:
                    self.hit_erased = True
                    return
                yield cell
                if cell.is_high_water_mark:
                    return
            return
        addr = self.top if mem_addr == 0 else mem_addr
        cell = self.memory.get(addr)
        if cell == ERASED:
            self.hit_erased = True
        elif cell is not None:
            yield cell

    async def async_stop(self):
        """Stop the read."""


def _load_from(memory, aldb=None):
    aldb = aldb or ALDB(Address("112233"))
    aldb._read_manager = ScriptedReadManager(memory)
    return aldb


class TestLoadingAnErasedAldb(unittest.TestCase):
    """Drive async_load through erased cells."""

    @async_case
    async def test_load_stays_partial_after_one_erased_cell_and_a_timeout(self):
        """One erased read followed by silence is not the end of the database."""
        memory = {addr: _real_record(addr) for addr in range(0x0FFF, 0x0FBF - 8, -8)}
        memory[0x0FB7] = ERASED
        memory[0x0FAF] = None
        aldb = _load_from(memory)
        status = await aldb.async_load()
        assert status == ALDBStatus.PARTIAL
        assert aldb.high_water_mark_mem_addr is None
        assert 0x0FAF not in aldb

    @async_case
    async def test_load_completes_after_a_run_of_erased_cells(self):
        """A long run of erased cells is the end of an i3 database."""
        memory = {0x0FFF: _real_record(0x0FFF), 0x0FF7: _real_record(0x0FF7)}
        for addr in range(0x0FEF, 0x0FEF - 8 * (MAX_CONSECUTIVE_ERASED + 2), -8):
            memory[addr] = ERASED
        aldb = _load_from(memory)
        status = await aldb.async_load()
        assert status == ALDBStatus.LOADED
        assert aldb.high_water_mark_mem_addr is not None
        assert aldb.high_water_mark_mem_addr < 0x0FF7

    @async_case
    async def test_load_reads_past_a_hole_to_the_real_high_water_mark(self):
        """An erased cell mid-database is a deleted slot, not the end."""
        memory = {
            0x0FFF: _real_record(0x0FFF),
            0x0FF7: ERASED,
            0x0FEF: _real_record(0x0FEF, controller=False),
            0x0FE7: _hwm_record(0x0FE7),
        }
        aldb = _load_from(memory)
        status = await aldb.async_load()
        assert status == ALDBStatus.LOADED
        assert aldb.high_water_mark_mem_addr == 0x0FE7
        assert not aldb[0x0FF7].is_in_use
        assert aldb[0x0FEF].is_in_use

    @async_case
    async def test_saved_first_record_above_top_of_memory_is_reset(self):
        """A database saved with phantom records heals on an ordinary load."""
        saved = {addr: _erased_record(addr) for addr in range(0xFFFC, 0xFFBC, -8)}
        saved[0x0FFF] = _real_record(0x0FFF)
        aldb = ALDB(Address("112233"))
        aldb.load_saved_records(ALDBStatus.PARTIAL, saved, 0xFFFC)
        assert aldb.first_mem_addr == 0xFFFC
        memory = {
            0x0FFF: _real_record(0x0FFF),
            0x0FF7: _real_record(0x0FF7, controller=False),
            0x0FEF: _hwm_record(0x0FEF),
        }
        _load_from(memory, aldb)
        status = await aldb.async_load()
        assert aldb.first_mem_addr == 0x0FFF
        assert status == ALDBStatus.LOADED
        assert max(aldb) == 0x0FFF

    @async_case
    async def test_first_record_response_above_top_of_memory_is_ignored(self):
        """A garbage first-record reply must not move the top of memory."""
        memory = {
            0xFFFC: _real_record(0xFFFC),
            0x0FFF: _real_record(0x0FFF),
            0x0FF7: _hwm_record(0x0FF7),
        }
        aldb = _load_from(memory)
        aldb._read_manager.top = 0xFFFC
        await aldb.async_load()
        assert aldb.first_mem_addr == 0x0FFF
        assert 0xFFFC not in aldb


if __name__ == "__main__":
    unittest.main()
