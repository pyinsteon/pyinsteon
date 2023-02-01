"""Test the ALDBReadManager."""
# import asyncio
import unittest

# from pyinsteon.address import Address
from pyinsteon.aldb.aldb import ALDB
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import EngineVersion
from pyinsteon.data_types.user_data import UserData
from pyinsteon.managers.aldb_read_manager import ALDBReadManager
from pyinsteon.topics import EXTENDED_READ_WRITE_ALDB

from tests import set_log_levels
from tests.utils import TopicItem, async_case, random_address, send_topics


def create_response_topic_item(address, record):
    """Return a response TopicItem for an ALDB record response."""
    ud_response = UserData({**(dict(record)), "d2": 0x01})
    response_topic = f"{address.id}.{EXTENDED_READ_WRITE_ALDB}"
    return TopicItem(
        response_topic,
        {
            "cmd1": 0x2F,
            "cmd2": 0,
            "user_data": ud_response,
            "target": record.target,
            "hops_left": 3,
        },
        0.1,
    )


class TestAldbReadManager(unittest.TestCase):
    """Test the ALDBReadManager."""

    def setUp(self):
        """Set up the TestAldbReadManager tests."""
        set_log_levels(logger="debug", logger_topics=True)

    @async_case
    async def test_read_one_standard(self):
        """Test reading one record using the standard method."""
        address = random_address()
        target = random_address()
        aldb = ALDB(address=address, version=EngineVersion.I2)
        mgr = ALDBReadManager(aldb=aldb)
        mem_addr = 0x0FFF

        mem_hi = mem_addr >> 8
        mem_lo = mem_addr & 0xFF
        user_data = UserData(
            {"d1": 0x00, "d2": 0x00, "d3": mem_hi, "d4": mem_lo, "d5": 1}
        )

        ack_topic = f"ack.{address.id}.{EXTENDED_READ_WRITE_ALDB}.direct"
        ack_topic_item = TopicItem(
            ack_topic, {"cmd1": 0x2F, "cmd2": 0, "user_data": user_data}, 0.5
        )

        dir_ack_topic = f"{address.id}.{EXTENDED_READ_WRITE_ALDB}.direct_ack"
        dir_ack_topic_item = TopicItem(
            dir_ack_topic,
            {
                "cmd1": 0x2F,
                "cmd2": 0,
                "target": target,
                "user_data": None,
                "hops_left": 3,
            },
            0.5,
        )

        record = ALDBRecord(
            memory=0x0FFF,
            controller=True,
            group=0,
            target=target,
            data1=1,
            data2=2,
            data3=3,
        )
        response_topic_item = create_response_topic_item(address, record)
        send_topics([ack_topic_item, dir_ack_topic_item, response_topic_item])
        test_record = None
        async for rec in mgr.async_read(mem_addr=mem_addr, num_recs=1):
            test_record = rec

        assert test_record.is_exact_match(record, test_in_use=True)

    @async_case
    async def test_read_all_standard(self):
        """Test reading all records using the standard method."""
        address = random_address()
        target = random_address()
        aldb = ALDB(address=address, version=EngineVersion.I2)
        mgr = ALDBReadManager(aldb=aldb)
        user_data = UserData({"d1": 0x00, "d2": 0x00, "d3": 0, "d4": 0, "d5": 0})

        ack_topic = f"ack.{address.id}.{EXTENDED_READ_WRITE_ALDB}.direct"
        ack_topic_item = TopicItem(
            ack_topic, {"cmd1": 0x2F, "cmd2": 0, "user_data": user_data}, 0.5
        )

        dir_ack_topic = f"{address.id}.{EXTENDED_READ_WRITE_ALDB}.direct_ack"
        dir_ack_topic_item = TopicItem(
            dir_ack_topic,
            {
                "cmd1": 0x2F,
                "cmd2": 0,
                "target": target,
                "user_data": None,
                "hops_left": 3,
            },
            0.5,
        )

        record_1 = ALDBRecord(
            memory=0x0FFF,
            controller=True,
            group=0,
            target=target,
            data1=1,
            data2=2,
            data3=3,
        )
        record_2 = ALDBRecord(
            memory=0x0FF7,
            controller=True,
            group=0,
            target=target,
            data1=1,
            data2=2,
            data3=3,
        )
        record_3 = ALDBRecord(
            memory=0x0FEF,
            controller=True,
            group=0,
            target=target,
            data1=1,
            data2=2,
            data3=3,
        )
        record_hwm = ALDBRecord(
            memory=0x0FE7,
            controller=True,
            group=0,
            target=target,
            data1=1,
            data2=2,
            data3=3,
        )
        records = [record_1, record_2, record_3, record_hwm]
        topic_items = [ack_topic_item, dir_ack_topic_item]
        for rec in records:
            topic_items.append(create_response_topic_item(address, rec))
        send_topics(topic_items)
        rec_num = 0
        async for rec in mgr.async_read():
            if rec is None:
                break
            assert rec.is_exact_match(records[rec_num])
            rec_num += 1
