"""Test the modem ALDB write manager."""

# pylint: disable=protected-access
import unittest

from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import (
    ManageAllLinkRecordAction,
    ReadWriteMode,
    ResponseStatus,
)
from pyinsteon.managers.aldb_im_write_manager import ImWriteManager

from tests.utils import async_case, random_address


class _FakeModemALDB:
    """Modem ALDB stand-in serving a fixed record list."""

    def __init__(self, records):
        """Init the _FakeModemALDB class."""
        self._record_list = records
        self.is_loaded = True
        self.read_write_mode = ReadWriteMode.STANDARD

    async def async_find_records(self, address, group):
        """Yield records matching the address and group."""
        for rec in self._record_list:
            if rec.target == address and rec.group == group:
                yield rec


class _FakeWriteCmd:
    """Capture the manage-all-link-record sends."""

    def __init__(self):
        """Init the _FakeWriteCmd class."""
        self.calls = []

    async def async_send(self, **kwargs):
        """Record the call and report success."""
        self.calls.append(kwargs)
        return ResponseStatus.SUCCESS


class TestImWriteManagerStandardDelete(unittest.TestCase):
    """Test the standard-mode delete path."""

    def _manager(self, modem_records):
        mgr = ImWriteManager(_FakeModemALDB(modem_records))
        mgr._write_cmd = _FakeWriteCmd()
        return mgr

    @async_case
    async def test_delete_sends_the_matching_record(self):
        """Deleting a record sends DELETE_FIRST for the record found."""
        target = random_address()
        existing = ALDBRecord(
            0x1FFF,
            controller=True,
            group=1,
            target=target,
            data1=2,
            data2=10,
            data3=44,
        )
        deleted = ALDBRecord(
            0x1FFF,
            controller=True,
            group=1,
            target=target,
            data1=2,
            data2=10,
            data3=44,
            in_use=False,
        )
        mgr = self._manager([existing])
        result = await mgr.async_write(deleted)
        assert result == ResponseStatus.SUCCESS
        assert len(mgr._write_cmd.calls) == 1
        call = mgr._write_cmd.calls[0]
        assert call["action"] == ManageAllLinkRecordAction.DELETE_FIRST
        assert call["group"] == 1
        assert call["target"] == target
        assert call["controller"]

    @async_case
    async def test_delete_without_a_matching_record_fails(self):
        """Deleting a record the modem does not hold sends nothing."""
        deleted = ALDBRecord(
            0x1FFF,
            controller=True,
            group=1,
            target=random_address(),
            data1=0,
            data2=0,
            data3=0,
            in_use=False,
        )
        mgr = self._manager([])
        result = await mgr.async_write(deleted)
        assert result == ResponseStatus.FAILURE
        assert not mgr._write_cmd.calls


if __name__ == "__main__":
    unittest.main()
