"""Test handling of i3 erased (0xFF) ALDB cells."""

# pylint: disable=protected-access
import unittest

from pyinsteon.address import Address
from pyinsteon.aldb.aldb import ALDB
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


if __name__ == "__main__":
    unittest.main()
