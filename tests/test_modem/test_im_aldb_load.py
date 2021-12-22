"""Test loading the IM ALDB."""
import asyncio
import unittest

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.aldb.modem_aldb import ModemALDB
from pyinsteon.topics import (
    ALL_LINK_RECORD_RESPONSE,
    GET_FIRST_ALL_LINK_RECORD,
    GET_NEXT_ALL_LINK_RECORD,
)
from tests import _LOGGER, set_log_levels
from tests.utils import TopicItem, async_case, random_address

SEND_FIRST_TOPIC = "send.{}".format(GET_FIRST_ALL_LINK_RECORD)
SEND_TOPIC = "send.{}".format(GET_NEXT_ALL_LINK_RECORD)
ACK_FIRST_TOPIC = "ack.{}".format(GET_FIRST_ALL_LINK_RECORD)
ACK_TOPIC = "ack.{}".format(GET_NEXT_ALL_LINK_RECORD)
NAK_FIRST_TOPIC = "nak.{}".format(GET_FIRST_ALL_LINK_RECORD)
NAK_TOPIC = "nak.{}".format(GET_NEXT_ALL_LINK_RECORD)
LOCK = asyncio.Lock()


def send_nak_response():
    """Send a NAK response."""
    pub.sendMessage(NAK_FIRST_TOPIC)


def fill_rec(flags, group, target, data1, data2, data3):
    """Fill an All-Link Record."""
    from pyinsteon.protocol.messages.all_link_record_flags import AllLinkRecordFlags

    kwargs = {
        "flags": AllLinkRecordFlags(flags),
        "group": group,
        "target": Address(target),
        "data1": data1,
        "data2": data2,
        "data3": data3,
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
        self.topics = [
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

    def send_response(self):
        """Send a response."""
        if self.record == 0:
            pub.sendMessage(ACK_FIRST_TOPIC)
        elif self.record < 8:
            pub.sendMessage(ACK_TOPIC)
        else:
            pub.sendMessage(NAK_TOPIC)
            return

        rec_item = self.topics[self.record]
        pub.sendMessage(rec_item.topic, **rec_item.kwargs)
        self.record += 1

    @async_case
    async def test_load_empty(self):
        """Test loading an empty modem ALDB."""
        async with LOCK:
            mgr = pub.getDefaultTopicMgr()
            mgr.delTopic(ALL_LINK_RECORD_RESPONSE)
            aldb = ModemALDB(random_address())
            pub.subscribe(send_nak_response, SEND_FIRST_TOPIC)

            response = await aldb.async_load()
            _LOGGER.debug("Done LOAD function.")
            _LOGGER.debug("Status: %s", response.name)
            assert aldb.is_loaded
            _LOGGER.debug("ALDB Record Count: %d", len(aldb))
            assert len(aldb) == 0
            pub.unsubscribe(send_nak_response, SEND_FIRST_TOPIC)

    @async_case
    async def test_load_8_records(self):
        """Test loading 8 records into the modem ALDB."""
        async with LOCK:
            mgr = pub.getDefaultTopicMgr()
            mgr.delTopic(ALL_LINK_RECORD_RESPONSE)
            pub.subscribe(self.send_response, SEND_FIRST_TOPIC)
            pub.subscribe(self.send_response, SEND_TOPIC)

            aldb = ModemALDB(random_address())
            response = await aldb.async_load()
            await asyncio.sleep(0.01)
            _LOGGER.debug("Done LOAD function.")
            _LOGGER.debug("Status: %s", response.name)
            assert aldb.is_loaded
            _LOGGER.debug("ALDB Record Count: %d", len(aldb))
            assert len(aldb) == 8
            pub.unsubscribe(self.send_response, SEND_FIRST_TOPIC)
            pub.unsubscribe(self.send_response, SEND_TOPIC)


if __name__ == "__main__":
    unittest.main()
