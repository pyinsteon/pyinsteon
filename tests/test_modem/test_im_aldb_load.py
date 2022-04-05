"""Test loading the IM ALDB."""
import asyncio
import unittest

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.aldb.modem_aldb import ModemALDB
from pyinsteon.constants import ReadWriteMode
from pyinsteon.topics import (
    ALL_LINK_RECORD_RESPONSE,
    GET_FIRST_ALL_LINK_RECORD,
    GET_NEXT_ALL_LINK_RECORD,
    READ_EEPROM,
    READ_EEPROM_RESPONSE,
)
from tests import _LOGGER, set_log_levels
from tests.utils import TopicItem, async_case, random_address

SEND_FIRST_TOPIC = "send.{}".format(GET_FIRST_ALL_LINK_RECORD)
SEND_NEXT_TOPIC = "send.{}".format(GET_NEXT_ALL_LINK_RECORD)
ACK_FIRST_TOPIC = "ack.{}".format(GET_FIRST_ALL_LINK_RECORD)
ACK_NEXT_TOPIC = "ack.{}".format(GET_NEXT_ALL_LINK_RECORD)
NAK_FIRST_TOPIC = "nak.{}".format(GET_FIRST_ALL_LINK_RECORD)
NAK_NEXT_TOPIC = "nak.{}".format(GET_NEXT_ALL_LINK_RECORD)

SEND_READ_EEPROM_TOPIC = "send.{}".format(READ_EEPROM)
ACK_EEPROM_TOPIC = "ack.{}".format(READ_EEPROM)
NAK_EEPROM_TOPIC = "nak.{}".format(READ_EEPROM)

LOCK = asyncio.Lock()


def send_nak_response():
    """Send a NAK response."""
    pub.sendMessage(NAK_FIRST_TOPIC)


def fill_rec(flags, group, target, data1, data2, data3):
    """Fill an All-Link Record."""
    from pyinsteon.data_types.all_link_record_flags import AllLinkRecordFlags

    kwargs = {
        "flags": AllLinkRecordFlags(flags),
        "group": group,
        "target": Address(target),
        "data1": data1,
        "data2": data2,
        "data3": data3,
    }
    return kwargs


def fill_eeprom_rec(mem_addr, flags, group, target, data1=0, data2=0, data3=0):
    """Fill an All-Link Record."""
    from pyinsteon.data_types.all_link_record_flags import AllLinkRecordFlags

    flags = AllLinkRecordFlags(flags)
    kwargs = {
        "mem_addr": mem_addr,
        "flags": flags,
        # "high_water_mark": flags.is_hwm,
        # "controller": flags.mode == AllLinkMode.CONTROLLER ,
        "group": group,
        "target": Address(target),
        "data1": data1,
        "data2": data2,
        "data3": data3,
        # "bit5": flags.is_bit_5_set,
        # "bit4": flags.is_bit_4_set,
    }
    return kwargs


class TestModemALDBLoad(unittest.TestCase):
    """Test the ModemALDB class."""

    def setUp(self):
        """Set up the test."""
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        _LOGGER.debug("Running setUp")
        self.record = 0
        addr = random_address()

        self.topics_standard = [
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x01, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x02, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x03, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x04, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x05, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x06, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x07, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                ALL_LINK_RECORD_RESPONSE,
                fill_rec(0x2E, 0x08, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
        ]

        self.topics_eeprom = [
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FFF, 0x2E, 0x01, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FF7, 0x2E, 0x02, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FEF, 0x2E, 0x03, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FE7, 0x2E, 0x04, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FDF, 0x2E, 0x05, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FD7, 0x2E, 0x06, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FCF, 0x2E, 0x07, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(0x1FC7, 0x2E, 0x08, addr.id, 0x02, 0x03, 0x04),
                0.2,
            ),
            TopicItem(
                READ_EEPROM_RESPONSE,
                fill_eeprom_rec(
                    0x1FBF, 0x00, 0x00, Address("000000"), 0x00, 0x00, 0x00
                ),
                0.2,
            ),
        ]

    def send_standard_response(self):
        """Send a response."""
        if self.record == 0:
            pub.sendMessage(ACK_FIRST_TOPIC)
        elif self.record < 8:
            pub.sendMessage(ACK_NEXT_TOPIC)
        else:
            pub.sendMessage(NAK_NEXT_TOPIC)
            return

        rec_item = self.topics_standard[self.record]
        pub.sendMessage(rec_item.topic, **rec_item.kwargs)
        self.record += 1

    def send_eeprom_response(self, mem_hi, mem_low):
        """Send a response."""
        pub.sendMessage(ACK_EEPROM_TOPIC, mem_hi=mem_hi, mem_low=mem_low)

        rec_item = self.topics_eeprom[self.record]
        pub.sendMessage(rec_item.topic, **rec_item.kwargs)
        self.record += 1

    @async_case
    async def test_load_standard_empty(self):
        """Test loading an empty modem ALDB."""
        async with LOCK:
            mgr = pub.getDefaultTopicMgr()
            mgr.delTopic(ALL_LINK_RECORD_RESPONSE)
            aldb = ModemALDB(random_address())
            aldb.read_write_mode = ReadWriteMode.STANDARD
            pub.subscribe(send_nak_response, SEND_FIRST_TOPIC)

            response = await aldb.async_load()
            _LOGGER.debug("Done LOAD function.")
            _LOGGER.debug("Status: %s", response.name)
            assert aldb.is_loaded
            _LOGGER.debug("ALDB Record Count: %d", len(aldb))
            assert len(aldb) == 0
            pub.unsubscribe(send_nak_response, SEND_FIRST_TOPIC)

    @async_case
    async def test_load_8_records_standard(self):
        """Test loading 8 records into the modem ALDB."""
        async with LOCK:
            mgr = pub.getDefaultTopicMgr()
            mgr.delTopic(ALL_LINK_RECORD_RESPONSE)
            pub.subscribe(self.send_standard_response, SEND_FIRST_TOPIC)
            pub.subscribe(self.send_standard_response, SEND_NEXT_TOPIC)

            aldb = ModemALDB(random_address())
            aldb.read_write_mode = ReadWriteMode.STANDARD
            response = await aldb.async_load()
            await asyncio.sleep(0.01)
            _LOGGER.debug("Done LOAD function.")
            _LOGGER.debug("Status: %s", response.name)
            assert aldb.is_loaded
            _LOGGER.debug("ALDB Record Count: %d", len(aldb))
            assert len(aldb) == 8
            pub.unsubscribe(self.send_standard_response, SEND_FIRST_TOPIC)
            pub.unsubscribe(self.send_standard_response, SEND_NEXT_TOPIC)

    @async_case
    async def test_load_8_records_eeprom(self):
        """Test loading 8 records into the modem ALDB."""
        async with LOCK:
            mgr = pub.getDefaultTopicMgr()
            mgr.delTopic(ALL_LINK_RECORD_RESPONSE)
            pub.subscribe(self.send_eeprom_response, SEND_READ_EEPROM_TOPIC)

            aldb = ModemALDB(random_address())
            aldb.read_write_mode = ReadWriteMode.EEPROM
            response = await aldb.async_load()
            await asyncio.sleep(0.01)
            _LOGGER.debug("Done LOAD function.")
            _LOGGER.debug("Status: %s", response.name)
            assert aldb.is_loaded
            _LOGGER.debug("ALDB Record Count: %d", len(aldb))
            assert len(aldb) == 9  # Includes HWM record
            pub.unsubscribe(self.send_standard_response, SEND_READ_EEPROM_TOPIC)


if __name__ == "__main__":
    unittest.main()
