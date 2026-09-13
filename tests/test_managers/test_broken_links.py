"""Test broken link detection across device databases."""

import unittest

from pyinsteon.aldb.aldb import ALDB
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.aldb.no_aldb import NoALDB
from pyinsteon.constants import ALDBStatus, LinkStatus
from pyinsteon.managers.link_manager import get_broken_links

from tests.utils import async_case, random_address


class _Device:
    """Stand-in device wrapping an ALDB."""

    def __init__(self, aldb):
        """Init the _Device class."""
        self.aldb = aldb
        self.address = aldb.address


def _loaded_aldb(address, record):
    hwm = ALDBRecord(
        0x0FF7,
        controller=False,
        group=0,
        target="000000",
        data1=0,
        data2=0,
        data3=0,
        in_use=False,
        high_water_mark=True,
    )
    aldb = ALDB(address)
    aldb.load_saved_records(
        ALDBStatus.LOADED, {0x0FFF: record, 0x0FF7: hwm}
    )
    return aldb


def _controller_rec(target, group=1, in_use=True):
    return ALDBRecord(
        0x0FFF,
        controller=True,
        group=group,
        target=target,
        data1=3,
        data2=0,
        data3=group,
        in_use=in_use,
    )


def _responder_rec(target, group=1, in_use=True):
    return ALDBRecord(
        0x0FFF,
        controller=False,
        group=group,
        target=target,
        data1=255,
        data2=28,
        data3=1,
        in_use=in_use,
    )


class TestBrokenLinks(unittest.TestCase):
    """Test get_broken_links against target database states."""

    @async_case
    async def test_link_to_no_aldb_device_is_not_broken(self):
        """A link to a device with no ALDB is not reported as broken."""
        addr_a = random_address()
        addr_b = random_address()
        dev_a = _Device(_loaded_aldb(addr_a, _controller_rec(addr_b)))
        dev_b = _Device(NoALDB(addr_b))
        broken = get_broken_links({addr_a: dev_a, addr_b: dev_b})
        assert broken == []

    @async_case
    async def test_deleted_target_record_does_not_satisfy_the_link(self):
        """A not-in-use record on the target does not complete the pair."""
        addr_a = random_address()
        addr_b = random_address()
        dev_a = _Device(_loaded_aldb(addr_a, _controller_rec(addr_b)))
        dev_b = _Device(_loaded_aldb(addr_b, _responder_rec(addr_a, in_use=False)))
        broken = get_broken_links({addr_a: dev_a, addr_b: dev_b})
        assert len(broken) == 1
        address, record, status = broken[0]
        assert address == addr_a
        assert record.mem_addr == 0x0FFF
        assert status == LinkStatus.MISSING_RESPONDER

    @async_case
    async def test_matching_in_use_records_are_not_broken(self):
        """A complete controller and responder pair reports nothing."""
        addr_a = random_address()
        addr_b = random_address()
        dev_a = _Device(_loaded_aldb(addr_a, _controller_rec(addr_b)))
        dev_b = _Device(_loaded_aldb(addr_b, _responder_rec(addr_a)))
        broken = get_broken_links({addr_a: dev_a, addr_b: dev_b})
        assert broken == []


if __name__ == "__main__":
    unittest.main()
