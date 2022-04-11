"""Test the device ALDB class."""
from unittest import TestCase

from pyinsteon.aldb import ALDB
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ALDBStatus, ALDBVersion, ResponseStatus
from pyinsteon.managers.aldb_write_manager import ALDBWriteException
from pyinsteon.topics import ALDB_VERSION
from pyinsteon.utils import publish_topic

from ..utils import async_case, random_address

modem_address = random_address()
records = {
    0x0FFF: ALDBRecord(
        0x0FFF,
        controller=True,
        group=0,
        target=modem_address,
        data1=1,
        data2=2,
        data3=3,
    ),
    0x0FF7: ALDBRecord(
        0x0FF7,
        controller=False,
        group=1,
        target=modem_address,
        data1=4,
        data2=5,
        data3=6,
    ),
    0x0FEF: ALDBRecord(
        0x0FEF,
        controller=False,
        group=0,
        target="000000",
        data1=0,
        data2=0,
        data3=0,
        in_use=False,
        high_water_mark=True,
    ),
}


class MockALDBWriteManager:
    """Mock the ALDBWriteManager."""

    response_status = ResponseStatus.SUCCESS
    exception_to_throw = None

    async def async_write(self, *args, **kwargs):
        """Mock the async_write method."""
        if self.exception_to_throw:
            raise self.exception_to_throw
        return self.response_status


class TestAldb(TestCase):
    """Test the device ALDB class."""

    def setup_aldb(self, aldb: ALDB, records: list, status=ALDBStatus.LOADED):
        """Set up an ALDB with records."""
        aldb.load_saved_records(status=status, records=records)

    def test_basic_properties(self):
        """Test the basic properties."""
        address = random_address()
        aldb = ALDB(address, version=ALDBVersion.V2CS, mem_addr=0x0AAA)
        assert aldb.address == address
        assert aldb.status == ALDBStatus.EMPTY
        assert aldb.version == ALDBVersion.V2CS
        assert aldb.first_mem_addr == 0x0AAA
        assert aldb.high_water_mark_mem_addr is None
        assert not aldb.is_loaded
        assert aldb.pending_changes == {}

    def test_update_version(self):
        """Test updating the ALDB version."""
        address = random_address()
        aldb = ALDB(address, version=ALDBVersion.V2CS)
        assert aldb.version == ALDBVersion.V2CS
        aldb.update_version(ALDBVersion.V2)
        assert aldb.version == ALDBVersion.V2
        publish_topic(f"{repr(address)}.{ALDB_VERSION}", version=1)
        assert aldb.version == ALDBVersion.V1

    def test_clear_pending(self):
        """Test the clear_pending method."""
        address = random_address()
        aldb = ALDB(address)
        aldb.add(group=1, target=random_address())
        assert len(aldb.pending_changes) == 1
        aldb.clear_pending()
        assert not aldb.pending_changes

    def test_load_saved_records(self):
        """Test the load_saved_records method."""
        address = random_address()
        aldb = ALDB(address)
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)
        assert aldb.status == ALDBStatus.LOADED
        assert len(aldb) == 3

    def test_set_load_status(self):
        """Test the load_saved_records method."""
        address = random_address()
        aldb = ALDB(address)
        self.setup_aldb(aldb, records, ALDBStatus.PARTIAL)
        assert aldb.status == ALDBStatus.PARTIAL
        aldb.set_load_status()
        assert aldb.status == ALDBStatus.LOADED

        no_hwm = {0x0FFF: records[0x0FFF], 0x0FF7: records[0x0FF7]}
        self.setup_aldb(aldb, no_hwm, ALDBStatus.LOADED)
        aldb.set_load_status()
        assert aldb.status == ALDBStatus.PARTIAL

        # record_gap = {0x0FFF: records[0x0FFF], 0x0FEF: records[0x0FEF]}
        self.setup_aldb(aldb, no_hwm, ALDBStatus.LOADED)
        aldb.set_load_status()
        assert aldb.status == ALDBStatus.PARTIAL

        self.setup_aldb(aldb, {}, ALDBStatus.LOADED)
        aldb.set_load_status()
        assert aldb.status == ALDBStatus.EMPTY

        hwm_rec = ALDBRecord(
            0x0FFF,
            controller=False,
            group=0,
            target="000000",
            data1=0,
            data2=0,
            data3=0,
            in_use=False,
            high_water_mark=True,
        )

        self.setup_aldb(aldb, {0x0FFF: hwm_rec}, ALDBStatus.LOADED)
        aldb.set_load_status()
        assert aldb.status == ALDBStatus.LOADED

    def test_remove(self):
        """Test the load_saved_records method."""
        address = random_address()
        aldb = ALDB(address)
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)
        aldb.remove(0x0FF7)
        rec = aldb.pending_changes.get(0x0FF7)
        assert rec
        assert rec.mem_addr == 0x0FF7
        assert not rec.is_in_use

    def test_modify(self):
        """Test the load_saved_records method."""
        address = random_address()
        aldb = ALDB(address)
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)

        orig_rec = aldb[0x0FF7]

        in_use = False
        group = orig_rec.group + 1
        controller = not orig_rec.is_controller
        target = random_address()
        data1 = orig_rec.data1 + 1
        data2 = orig_rec.data1 + 1
        data3 = orig_rec.data1 + 1

        aldb.modify(
            mem_addr=0x0FF7,
            in_use=in_use,
            group=group,
            controller=controller,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        new_rec = aldb.pending_changes.get(0x0FF7)
        assert new_rec
        assert new_rec.mem_addr == 0x0FF7
        assert new_rec.is_in_use == in_use
        assert new_rec.is_controller == controller
        assert new_rec.group == group
        assert new_rec.is_high_water_mark == orig_rec.is_high_water_mark
        assert new_rec.data1 == data1
        assert new_rec.data2 == data2
        assert new_rec.data3 == data3

        aldb.modify(
            mem_addr=0x0FF7,
            group=group,
            controller=controller,
            data2=data2,
        )
        new_rec = aldb.pending_changes.get(0x0FF7)
        assert new_rec
        assert new_rec.mem_addr == 0x0FF7
        assert new_rec.group == group
        assert new_rec.is_controller == controller
        assert new_rec.data2 == data2

        assert new_rec.is_in_use == orig_rec.is_in_use
        assert new_rec.is_high_water_mark == orig_rec.is_high_water_mark
        assert new_rec.data1 == orig_rec.data1
        assert new_rec.data3 == orig_rec.data3

    @async_case
    async def test_async_write(self):
        """Test the async_write method."""
        mock_writer = MockALDBWriteManager()
        address = random_address()
        aldb = ALDB(address)
        aldb._write_manager = mock_writer
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)

        aldb.add(group=1, target=random_address())
        success, failure = await aldb.async_write()
        assert success == 1
        assert failure == 0
        new_rec = aldb[0x0FEF]
        hwm_rec = aldb[0x0FE7]
        assert new_rec.group == 1
        assert hwm_rec
        assert hwm_rec.is_high_water_mark

        aldb.add(group=2, target=random_address())
        mock_writer.response_status = ResponseStatus.FAILURE
        success, failure = await aldb.async_write()
        assert success == 0
        assert failure == 1

        aldb.modify(mem_addr=0x0FEF, group=255, target=random_address())
        mock_writer.response_status = ResponseStatus.SUCCESS
        success, failure = await aldb.async_write()
        assert success == 2
        assert failure == 0

        mod_rec = aldb[0x0FEF]
        new_rec = aldb[0x0FE7]
        hwm_rec = aldb[0x0FDF]
        assert mod_rec.group == 255
        assert new_rec.group == 2
        assert hwm_rec
        assert hwm_rec.is_high_water_mark

        aldb.modify(mem_addr=0x0FEF, group=100, target=random_address())
        mock_writer.exception_to_throw = ALDBWriteException
        success, failure = await aldb.async_write()
        assert success == 0
        assert failure == 1

        self.setup_aldb(aldb, records, ALDBStatus.PARTIAL)
        aldb.add(group=2, target=random_address())
        success, failure = await aldb.async_write()
        assert success == 0
        assert failure == 1

        aldb.add(group=2, target=random_address())
        success, failure = await aldb.async_write(force=True)
        assert success == 1
        assert failure == 0
