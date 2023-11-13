"""Test the ALDBReadManager."""
import asyncio
from random import randint
import unittest

import async_timeout

from pyinsteon.address import Address
from pyinsteon.aldb.aldb_record import ALDBRecord
from pyinsteon.constants import ReadWriteMode
from pyinsteon.data_types.user_data import UserData
from pyinsteon.managers.aldb_read_manager import ALDBReadManager
from pyinsteon.topics import EXTENDED_READ_WRITE_ALDB, PEEK, SET_ADDRESS_MSB

from tests import set_log_levels
from tests.utils import TopicItem, async_case, random_address, send_topics

MODEM_ADDRESS = random_address()


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
        0.2,
    )


def gen_records(num_recs):
    """Generate a set of ALDB records."""
    last_mem_addr = 0x0FFF - 8 * (num_recs - 1)
    records = []
    for mem_addr in range(0x0FFF, last_mem_addr, -8):
        record = ALDBRecord(
            memory=mem_addr,
            controller=bool(randint(0, 1)),
            group=randint(0, 254),
            target=random_address(),
            data1=randint(0, 254),
            data2=randint(0, 254),
            data3=randint(0, 254),
        )
        records.append(record)

    hwm_mem_addr = records[-1].mem_addr - 8
    record_hwm = ALDBRecord(
        memory=hwm_mem_addr,
        controller=True,
        group=0,
        target=Address("000000"),
        data1=0,
        data2=0,
        data3=0,
        high_water_mark=True,
        bit4=False,
        bit5=False,
    )
    records.append(record_hwm)
    return records


def gen_peek_topic_items(address, record):
    """Generate the PEEK command topics from an ALDB record."""
    topic_items = []
    mem_hi = record.mem_addr >> 8
    mem_lo = record.mem_addr & 0xFF

    msb_ack_topic = f"ack.{address.id}.{SET_ADDRESS_MSB}.direct"
    msb_dir_ack_topic = f"{address.id}.{SET_ADDRESS_MSB}.direct_ack"
    rec_bytes = bytearray(
        [
            record.data3,
            record.data2,
            record.data1,
            record.target.low,
            record.target.middle,
            record.target.high,
            record.group,
            record.control_flags,
        ]
    )
    for curr_byte in range(0, 8):
        topic_items.append(
            TopicItem(
                msb_ack_topic, {"cmd1": 0x28, "cmd2": mem_hi, "user_data": None}, 0.2
            )
        )
        topic_items.append(
            TopicItem(
                msb_dir_ack_topic,
                {
                    "cmd1": 0x28,
                    "cmd2": mem_hi,
                    "target": MODEM_ADDRESS,
                    "user_data": None,
                    "hops_left": 3,
                },
                0.2,
            )
        )
        peek_ack_topic = f"ack.{address.id}.{PEEK}.direct"
        topic_items.append(
            TopicItem(
                peek_ack_topic,
                {"cmd1": 0x2B, "cmd2": mem_lo - curr_byte, "user_data": None},
                0.2,
            )
        )
        peek_dir_ack_topic = f"{address.id}.{PEEK}.direct_ack"
        topic_items.append(
            TopicItem(
                peek_dir_ack_topic,
                {
                    "cmd1": 0x2B,
                    "cmd2": rec_bytes[curr_byte],
                    "target": MODEM_ADDRESS,
                    "user_data": None,
                    "hops_left": 3,
                },
                0.2,
            )
        )
    return topic_items


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
        mgr = ALDBReadManager(address=address, first_record=0x0FFF)
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
                "target": MODEM_ADDRESS,
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
        mgr = ALDBReadManager(address=address, first_record=0x0FFF)
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
                "target": MODEM_ADDRESS,
                "user_data": None,
                "hops_left": 3,
            },
            0.5,
        )
        records = gen_records(num_recs=randint(10, 100))
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
            if rec.is_high_water_mark:
                await mgr.async_stop()
        assert rec_num == len(records)

    @async_case
    async def test_read_one_peek(self):
        """Test reading one record using the PEEK method."""

        address = random_address()
        target = random_address()
        mgr = ALDBReadManager(address=address, first_record=0x0FFF)

        record = ALDBRecord(
            memory=0x0FFF,
            controller=True,
            group=0,
            target=target,
            data1=1,
            data2=2,
            data3=3,
        )
        topic_items = gen_peek_topic_items(address=address, record=record)
        send_topics(topic_items)

        async for rec in mgr.async_read(
            mem_addr=record.mem_addr,
            num_recs=1,
            read_write_mode=ReadWriteMode.PEEK_POKE,
        ):
            assert rec.is_exact_match(record)

    @async_case
    async def test_read_all_peek(self):
        """Test reading all records using the PEEK method."""

        address = random_address()
        mgr = ALDBReadManager(address=address, first_record=0x0FFF)

        records = gen_records(3)
        all_topic_items = []
        for record in records:
            topic_items = gen_peek_topic_items(address=address, record=record)
            all_topic_items.extend(topic_items)
        send_topics(all_topic_items)

        rec_num = 0
        async for rec in mgr.async_read(
            mem_addr=0,
            num_recs=0,
            read_write_mode=ReadWriteMode.PEEK_POKE,
        ):
            assert rec.is_exact_match(records[rec_num])
            rec_num += 1
            if rec.is_high_water_mark:
                await mgr.async_stop()

    @async_case
    async def test_read_all_standard_direct_nak(self):
        """Test reading all records using the standard method with a Direct NAK response."""
        address = random_address()
        mgr = ALDBReadManager(address=address, first_record=0x0FFF)
        user_data = UserData({"d1": 0x00, "d2": 0x00, "d3": 0, "d4": 0, "d5": 0})

        ack_topic = f"ack.{address.id}.{EXTENDED_READ_WRITE_ALDB}.direct"
        ack_topic_item = TopicItem(
            ack_topic, {"cmd1": 0x2F, "cmd2": 0, "user_data": user_data}, 0.5
        )

        dir_nak_topic = f"{address.id}.{EXTENDED_READ_WRITE_ALDB}.direct_nak"
        dir_nak_topic_item = TopicItem(
            dir_nak_topic,
            {
                "cmd1": 0x2F,
                "cmd2": 0xFD,
                "target": MODEM_ADDRESS,
                "user_data": None,
                "hops_left": 3,
            },
            0.5,
        )
        topic_items = [ack_topic_item, dir_nak_topic_item]

        send_topics(topic_items)
        async with async_timeout.timeout(3):
            try:
                async for _ in mgr.async_read():
                    assert False
            except asyncio.TimeoutError:
                assert False

    @async_case
    async def test_read_one_standard_direct_nak(self):
        """Test reading one record using the standard method with a direct NAK."""
        address = random_address()
        mgr = ALDBReadManager(address=address, first_record=0x0FFF)
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

        dir_nak_topic = f"{address.id}.{EXTENDED_READ_WRITE_ALDB}.direct_nak"
        dir_nak_topic_item = TopicItem(
            dir_nak_topic,
            {
                "cmd1": 0x2F,
                "cmd2": 0xFB,
                "target": MODEM_ADDRESS,
                "user_data": None,
                "hops_left": 3,
            },
            0.5,
        )

        send_topics([ack_topic_item, dir_nak_topic_item])

        async with async_timeout.timeout(3):
            try:
                async for _ in mgr.async_read(mem_addr=mem_addr, num_recs=1):
                    assert False
            except asyncio.TimeoutError:
                assert False

    @async_case
    async def test_read_one_peek_direct_nak(self):
        """Test peek record with direct nak response."""

        address = random_address()
        target = random_address()
        mgr = ALDBReadManager(address=address, first_record=0x0FFF)

        record = ALDBRecord(
            memory=0x0FFF,
            controller=True,
            group=0,
            target=target,
            data1=1,
            data2=2,
            data3=3,
        )
        mem_hi = record.mem_addr >> 8

        msb_ack_topic = f"ack.{address.id}.{SET_ADDRESS_MSB}.direct"
        ack_topic = TopicItem(
            msb_ack_topic, {"cmd1": 0x28, "cmd2": mem_hi, "user_data": None}, 0.5
        )
        msb_dir_nak_topic = f"{address.id}.{SET_ADDRESS_MSB}.direct_nak"
        nak_response_topic = TopicItem(
            msb_dir_nak_topic,
            {
                "cmd1": 0x28,
                "cmd2": 0xFF,
                "target": target.id,
                "hops_left": 3,
                "user_data": None,
            },
            0.5,
        )
        send_topics([ack_topic, nak_response_topic])

        async with async_timeout.timeout(3):
            try:
                async for _ in mgr.async_read(
                    mem_addr=record.mem_addr,
                    num_recs=1,
                    read_write_mode=ReadWriteMode.PEEK_POKE,
                ):
                    assert False
            except asyncio.TimeoutError:
                assert False
