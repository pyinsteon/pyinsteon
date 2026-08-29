"""Test the modem ALDB."""

# pylint: disable=protected-access
import asyncio
from unittest import TestCase
from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.aldb import modem_aldb
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ALDBStatus, ReadWriteMode, ResponseStatus
from pyinsteon.topics import ALL_LINK_RECORD_RESPONSE

from pyinsteon.aldb.modem_aldb import ModemALDB

from ..utils import async_case, random_address


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


class MockEepromReader:
    """Serve modem EEPROM records and fail the addresses it is told to."""

    def __init__(self, hwm_addr=0x1FE7, fail_once=None, fail_always=None):
        """Init the MockEepromReader class."""
        self.hwm_addr = hwm_addr
        self.fail_once = set(fail_once or [])
        self.fail_always = set(fail_always or [])
        self.reads = []

    async def async_read_record(self, mem_addr):
        """Return the record at mem_addr."""
        self.reads.append(mem_addr)
        if mem_addr in self.fail_always:
            return None
        if mem_addr in self.fail_once:
            self.fail_once.remove(mem_addr)
            return None
        if mem_addr < self.hwm_addr:
            return None
        return _record(mem_addr, high_water_mark=mem_addr == self.hwm_addr)


class GatedEepromReader(MockEepromReader):
    """Hold every read until released."""

    def __init__(self, **kwargs):
        """Init the GatedEepromReader class."""
        super().__init__(**kwargs)
        self.release = asyncio.Event()

    async def async_read_record(self, mem_addr):
        """Return the record at mem_addr once released."""
        await self.release.wait()
        return await super().async_read_record(mem_addr)


class RecordingWriter:
    """Accept every write and remember it."""

    def __init__(self):
        """Init the RecordingWriter class."""
        self.writes = []

    async def async_write(self, record, force=False):
        """Record the write and report success."""
        self.writes.append(record)
        return ResponseStatus.SUCCESS


# pypubsub holds weak references to the subscribed handlers
_SUBSCRIBED = []


def _eeprom_aldb(reader):
    aldb = ModemALDB(random_address(), mem_addr=0x1FFF)
    if aldb._read_manager is not None:
        _SUBSCRIBED.append(aldb._read_manager)
    aldb._read_write_mode = ReadWriteMode.EEPROM
    aldb._read_manager = reader
    return aldb


class TestModemALDB(TestCase):
    """Test the modem ALDB."""

    @async_case
    async def test_one_modem(self):
        """Test only one modem can receive records."""
        mgr = pub.getDefaultTopicMgr()
        topic = mgr.getTopic(ALL_LINK_RECORD_RESPONSE, okIfNone=True)

        # Check if there is already one listner. If there is,
        # then we should still only have one at the end
        if topic:
            listeners = topic.getListeners()
            has_listeners = len(listeners) != 0
        else:
            has_listeners = False

        modem_aldb_1 = ModemALDB(random_address())
        modem_aldb_2 = ModemALDB(random_address())
        if has_listeners:
            assert modem_aldb_1._read_manager is None
        else:
            print
            print(modem_aldb_1._read_manager)
            print(modem_aldb_2._read_manager)
            assert modem_aldb_1._read_manager is not None
        assert modem_aldb_2._read_manager is None

        topic = mgr.getTopic(ALL_LINK_RECORD_RESPONSE)
        listeners = topic.getListeners()
        assert len(listeners) == 1

    @async_case
    async def test_missed_record_is_reread(self):
        """Test a record that fails once is read again."""
        reader = MockEepromReader(fail_once=[0x1FF7])
        aldb = _eeprom_aldb(reader)

        await aldb.async_load()

        assert aldb.status == ALDBStatus.LOADED
        assert sorted(aldb) == [0x1FE7, 0x1FEF, 0x1FF7, 0x1FFF]
        assert reader.reads.count(0x1FF7) == 2

    @async_case
    async def test_unreadable_record_does_not_end_the_walk(self):
        """Test the walk continues past a record that never reads."""
        reader = MockEepromReader(fail_always=[0x1FF7])
        aldb = _eeprom_aldb(reader)

        await aldb.async_load()

        assert aldb.status == ALDBStatus.PARTIAL
        assert 0x1FF7 not in aldb
        assert 0x1FE7 in aldb

    @async_case
    async def test_walk_stops_at_the_high_water_mark(self):
        """Test no record below the high water mark is stored."""
        reader = MockEepromReader()
        aldb = _eeprom_aldb(reader)

        await aldb.async_load()

        assert aldb.status == ALDBStatus.LOADED
        assert min(aldb) == 0x1FE7
        assert 0x1FDF not in reader.reads

    @async_case
    async def test_incomplete_read_keeps_the_saved_records(self):
        """Test a read with no high water mark leaves the saved records alone."""
        saved = {addr: _record(addr) for addr in (0x1FFF, 0x1FF7, 0x1FEF)}
        saved[0x1FE7] = _record(0x1FE7, high_water_mark=True)
        reader = MockEepromReader(fail_always=[0x1FFF, 0x1FF7, 0x1FEF])
        aldb = _eeprom_aldb(reader)
        aldb.load_saved_records(ALDBStatus.LOADED, saved)

        await aldb.async_load()

        assert len(aldb) == 4

    @async_case
    async def test_incomplete_read_keeps_pending_changes(self):
        """Test a re-read that dies partway keeps changes not yet written."""
        aldb = _eeprom_aldb(MockEepromReader())
        await aldb.async_load()
        assert aldb.status == ALDBStatus.LOADED
        aldb.add(group=1, target=random_address(), controller=True)
        assert len(aldb.pending_changes) == 1

        aldb._read_manager = MockEepromReader(fail_always=[0x1FF7])
        await aldb.async_load(refresh=True)

        assert aldb.status == ALDBStatus.LOADED
        assert len(aldb.pending_changes) == 1

    @async_case
    async def test_incomplete_read_keeps_an_equal_sized_saved_set(self):
        """Test a same size read with no high water mark keeps the saved records."""
        saved = {
            addr: ALDBRecord(
                memory=addr,
                controller=True,
                group=7,
                target=Address("010203"),
                data1=0,
                data2=0,
                data3=0,
                in_use=True,
                high_water_mark=False,
            )
            for addr in (0x1FFF, 0x1FF7)
        }
        reader = MockEepromReader(fail_always=[0x1FEF, 0x1FE7, 0x1FDF])
        aldb = _eeprom_aldb(reader)
        aldb.load_saved_records(ALDBStatus.LOADED, saved)

        await aldb.async_load()

        assert len(aldb) == 2
        assert all(aldb[addr].group == 7 for addr in aldb)

    @async_case
    async def test_concurrent_loads_read_once(self):
        """Test a second load does not repeat a finished read."""
        reader = GatedEepromReader()
        aldb = _eeprom_aldb(reader)

        first = asyncio.ensure_future(aldb.async_load())
        second = asyncio.ensure_future(aldb.async_load())
        await asyncio.sleep(0.01)
        reader.release.set()
        await asyncio.gather(first, second)

        assert aldb.status == ALDBStatus.LOADED
        assert reader.reads == [0x1FFF, 0x1FF7, 0x1FEF, 0x1FE7]

    @async_case
    async def test_write_waits_for_a_load_in_progress(self):
        """Test a write issued during a load runs once the load is done."""
        reader = GatedEepromReader()
        aldb = _eeprom_aldb(reader)
        writer = RecordingWriter()
        aldb._write_manager = writer

        load = asyncio.ensure_future(aldb.async_load())
        await asyncio.sleep(0.01)
        assert aldb.status == ALDBStatus.LOADING

        aldb.add(group=1, target=random_address(), controller=True)
        write = asyncio.ensure_future(aldb.async_write())
        await asyncio.sleep(0.01)
        assert not writer.writes

        reader.release.set()
        await load
        assert await write == (1, 0)
        assert writer.writes[0].mem_addr == 0x1FE7
        assert not aldb.pending_changes
