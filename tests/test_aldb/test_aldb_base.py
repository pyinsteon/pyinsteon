"""Test the device ALDB base class."""
import asyncio
from random import randint
from unittest import TestCase

from pyinsteon import pub
from pyinsteon.aldb import ALDB
from pyinsteon.aldb.aldb_base import HWM_RECORD
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ALDBStatus, ALDBVersion, ResponseStatus
from pyinsteon.managers.aldb_write_manager import ALDBWriteException
from pyinsteon.topics import (
    ALDB_VERSION,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_CONTROLLER_REMOVED,
    DEVICE_LINK_RESPONDER_REMOVED,
    DEVICE_LINK_CONTROLLER_CREATED,
)
from pyinsteon.utils import publish_topic

from .. import set_log_levels
from ..utils import async_case, random_address

modem_address = random_address()
rec_0fff = ALDBRecord(
    0x0FFF,
    controller=True,
    group=0,
    target=random_address(),
    data1=1,
    data2=2,
    data3=3,
)
rec_0ff7 = ALDBRecord(
    0x0FF7,
    controller=False,
    group=1,
    target=modem_address,
    data1=4,
    data2=5,
    data3=6,
)
rec_hwm = ALDBRecord(
    0x0FEF,
    controller=False,
    group=0,
    target="000000",
    data1=0,
    data2=0,
    data3=0,
    in_use=False,
    high_water_mark=True,
)
records = {
    0x0FFF: rec_0fff,
    0x0FF7: rec_0ff7,
    0x0FEF: rec_hwm,
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


class TestAldbBase(TestCase):
    """Test the device ALDB base class."""

    def setup_aldb(
        self, aldb: ALDB, records: list, status=ALDBStatus.LOADED, first_mem_addr=None
    ):
        """Set up an ALDB with records."""
        aldb.load_saved_records(
            status=status, records=records, first_mem_addr=first_mem_addr
        )

    @async_case
    async def test_basic_properties(self):
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

        try:
            aldb[0x0F00] = "Not a record"
            assert False
        except ValueError:
            assert True

        aldb[0] = rec_0fff
        rec = aldb.pending_changes[-1]
        assert rec
        assert rec.mem_addr == 0

        aldb[0x0FEF] = rec_0fff
        rec = aldb.pending_changes[0x0FEF]
        assert rec
        assert rec.mem_addr == 0x0FEF
        aldb_repr = repr(aldb)
        assert aldb_repr.find("_records") != -1

        rec_0fff.mem_addr = 0x0FFF
        self.setup_aldb(aldb, records)
        for mem_addr in aldb:
            assert mem_addr in records.keys()
        assert aldb.high_water_mark_mem_addr == 0x0FEF

        rec = aldb.get(0x0FFF)
        assert rec
        assert rec.mem_addr == 0x0FFF

    @async_case
    async def test_update_version(self):
        """Test updating the ALDB version."""
        address = random_address()
        aldb = ALDB(address, version=ALDBVersion.V2CS)
        assert aldb.version == ALDBVersion.V2CS
        aldb.update_version(ALDBVersion.V2)
        assert aldb.version == ALDBVersion.V2
        publish_topic(f"{repr(address)}.{ALDB_VERSION}", version=1)
        assert aldb.version == ALDBVersion.V1

    @async_case
    async def test_clear_pending(self):
        """Test the clear_pending method."""
        address = random_address()
        aldb = ALDB(address)
        aldb.add(group=1, target=random_address())
        assert len(aldb.pending_changes) == 1
        aldb.clear_pending()
        assert not aldb.pending_changes

    @async_case
    async def test_load_saved_records(self):
        """Test the load_saved_records method."""
        address = random_address()
        aldb = ALDB(address)
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)
        assert aldb.status == ALDBStatus.LOADED
        assert len(aldb) == 3

        self.setup_aldb(aldb, records, ALDBStatus.LOADED, first_mem_addr=0x0aaa)
        assert aldb.first_mem_addr == 0x0aaa

    @async_case
    async def test_set_load_status(self):
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

        self.setup_aldb(aldb, records, ALDBStatus.LOADING)
        assert aldb.is_loaded

    @async_case
    async def test_add(self):
        """Test the add method."""
        address = random_address()
        aldb = ALDB(address)
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)
        # Test minimal add
        group = randint(0, 255)
        target = random_address()
        aldb.add(group=group, target=target)
        rec = aldb.pending_changes[-1]
        assert rec
        assert rec.mem_addr == 0x000
        assert rec.target == target
        assert rec.group == group
        assert not rec.is_controller
        assert rec.is_in_use
        assert rec.data1 == 0
        assert rec.data2 == 0
        assert rec.data3 == 0
        assert rec.is_bit5_set
        assert not rec.is_bit4_set
        
        # Test full add
        group = randint(0, 255)
        controller = True
        data1 = randint(0, 255)
        data2 = randint(0, 255)
        data3 = randint(0, 255)
        bit5 = False
        bit4 = True
        aldb.add(group=group, target=target, controller=controller, data1=data1, data2=data2, data3=data3, bit5=bit5, bit4=bit4)
        rec = aldb.pending_changes[-2]
        assert rec
        assert rec.mem_addr == 0x000
        assert rec.target == target
        assert rec.group == group
        assert rec.is_controller == controller
        assert rec.is_in_use
        assert rec.data1 == data1
        assert rec.data2 == data2
        assert rec.data3 == data3
        assert not rec.is_bit5_set
        assert rec.is_bit4_set
        
        # Test "add" with same group, target and mode
        rec = aldb[0x0ff7]
        data1 = randint(100, 255)
        data2 = randint(100, 255)
        data3 = randint(100, 255)
        aldb.add(group=rec.group, target=rec.target, controller=rec.is_controller, data1=data1, data2=data2, data3=data3)
        new_rec = aldb.pending_changes[rec.mem_addr]
        assert new_rec
        assert new_rec.mem_addr == rec.mem_addr
        assert new_rec.data1 == data1
        assert new_rec.data2 == data2
        assert new_rec.data3 == data3   

    @async_case
    async def test_remove(self):
        """Test the load_saved_records method."""
        address = random_address()
        aldb = ALDB(address)
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)
        aldb.remove(0x0FF7)
        rec = aldb.pending_changes.get(0x0FF7)
        assert rec
        assert rec.mem_addr == 0x0FF7
        assert not rec.is_in_use
        
        try:
            aldb.remove(0xffff)
            assert False
        except IndexError:
            assert True

    @async_case
    async def test_modify(self):
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
        
        try:
            aldb.modify(
            mem_addr=0xFFFF,  # Does not exist
            group=group,
            )
            assert False
        except IndexError:
            assert True

    @async_case
    async def test_find(self):
        """Test the find method."""
        aldb = ALDB(random_address())
        self.setup_aldb(aldb, records)
        for rec in aldb.find(target=rec_0ff7.target):
            assert rec.target == rec_0ff7.target
            
        try:
            for rec in aldb.find():
                assert False       
        except ValueError:
            assert True

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

    @async_case
    async def test_write_force(self):
        """Test the write method with force option."""
        mock_writer = MockALDBWriteManager()
        address = random_address()
        aldb = ALDB(address)
        aldb._write_manager = mock_writer
        self.setup_aldb(aldb, records, ALDBStatus.LOADED)

        aldb.add(group=1, target=random_address())
        success, failure = await aldb.async_write(force=True)
        assert success == 1
        assert failure == 0

        rec_0fef = ALDBRecord(
            0x0FEF,
            controller=False,
            group=1,
            target=modem_address,
            data1=4,
            data2=5,
            data3=6,
        )
        rec_hwm_0fe7 = ALDBRecord(
            0x0FE7,
            controller=False,
            group=0,
            target="000000",
            data1=0,
            data2=0,
            data3=0,
            in_use=False,
            high_water_mark=True,
        )
        recs_missing_0ff7 = {0x0FFF: rec_0fff, 0x0FEF: rec_0fef, 0x0FE7: rec_hwm_0fe7}

        self.setup_aldb(aldb, recs_missing_0ff7, ALDBStatus.PARTIAL)
        aldb.add(group=2, target=random_address())
        success, failure = await aldb.async_write(force=True)
        assert success == 1
        assert failure == 0
        rec = aldb[0x0FF7]
        assert rec
        assert rec.group == 2

        # Test when missing HWM record
        recs_missing_hwm = {0x0FFF: rec_0fff, 0x0ff7: rec_0ff7}

        self.setup_aldb(aldb, recs_missing_hwm, ALDBStatus.PARTIAL)
        group = randint(0, 255)
        target = random_address()
        aldb.add(group=group, target=target)
        success, failure = await aldb.async_write(force=True)
        assert success == 1
        assert failure == 0
        rec = aldb[0x0Fef]
        assert rec
        assert rec.group == group
        assert rec.target == target

    @async_case
    async def test_get_responders(self):
        """Test the get_responders method."""
        aldb = ALDB(random_address())
        self.setup_aldb(aldb, records)
        found = False
        for target in aldb.get_responders(rec_0fff.group):
            found = True
            assert target == rec_0fff.target
        assert found

    @async_case
    async def test_subscribe_status_changed(self):
        """Test subscribing to status change."""
        status_changed = False

        def handle_status_changed():
            """Handle status changed."""
            nonlocal status_changed
            status_changed = True

        aldb = ALDB(random_address())
        aldb.subscribe_status_changed(handle_status_changed)
        self.setup_aldb(aldb, records)
        await asyncio.sleep(0.1)
        assert status_changed

    @async_case
    async def test_subscribe_record_change(self):
        """Test the subscribe_record_changed method."""
        expected_topic = None
        expected_group = None
        expected_responder = None
        expected_controller = None
        call_count = 0

        def handle_record_changed(controller, responder, group, topic=pub.AUTO_TOPIC):
            """Handle the adding and removing of records."""
            nonlocal call_count
            call_count += 1
            assert topic.name.split(".")[0] == expected_topic
            assert group == expected_group
            assert controller == expected_controller
            assert responder == expected_responder

        mock_writer = MockALDBWriteManager()
        set_log_levels(logger_topics=True)
        aldb = ALDB(random_address())
        aldb._write_manager = mock_writer
        self.setup_aldb(aldb, records)
        aldb.subscribe_record_changed(handle_record_changed)
        target = random_address()

        # Create controller
        expected_group = 12
        expected_topic = DEVICE_LINK_CONTROLLER_CREATED
        expected_controller = aldb.address
        expected_responder = target
        aldb.add(group=expected_group, target=target, controller=True)
        await aldb.async_write()
        await asyncio.sleep(0.1)
        assert call_count == 1

        # Remove controller
        rec = aldb[0x0FEF]
        assert rec.target == target  # Make sure we have the right record
        assert rec.is_controller
        aldb.remove(mem_addr=rec.mem_addr)
        call_count = 0
        expected_topic = DEVICE_LINK_CONTROLLER_REMOVED
        await aldb.async_write()
        await asyncio.sleep(0.1)
        assert call_count == 1

        # Create responder
        call_count = 0
        expected_controller = target
        expected_responder = aldb.address
        expected_group = 22
        expected_topic = DEVICE_LINK_RESPONDER_CREATED
        aldb.add(group=expected_group, target=target, controller=False)
        await aldb.async_write()
        await asyncio.sleep(0.1)
        assert call_count == 1

        # Remove responder
        rec = aldb[0x0FEF]
        assert rec.target == target  # Make sure we have the right record
        assert not rec.is_controller
        aldb.remove(mem_addr=rec.mem_addr)
        call_count = 0
        expected_topic = DEVICE_LINK_RESPONDER_REMOVED
        await aldb.async_write()
        await asyncio.sleep(0.1)
        assert call_count == 1
