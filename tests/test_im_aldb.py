"""Test loading the IM ALDB."""
import unittest

from pyinsteon.address import Address
from pyinsteon.aldb import ModemALDB
from pyinsteon.topics import (ALL_LINK_RECORD_RESPONSE, GET_NEXT_ALL_LINK_RECORD,
                              GET_FIRST_ALL_LINK_RECORD)
from tests.utils import TopicItem, async_case, send_topics
from tests import _LOGGER, set_log_levels


def fill_rec(flags, group, address, data1, data2, data3):
    """Fill an All-Link Record."""
    from pyinsteon.protocol.messages.all_link_record_flags import AllLinkRecordFlags
    kwargs = {'flags': AllLinkRecordFlags(flags),
              'group': group,
              'address': Address(address),
              'data1': data1,
              'data2': data2,
              'data3': data3}
    return kwargs


class TestModemALDB(unittest.TestCase):
    """Test the ModemALDB class."""

    def setUp(self):
        """Setup the test."""
        set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='info')
        self.address = Address('000000')
        self.aldb = ModemALDB(self.address)

    @async_case
    async def test_load(self):
        """Test loading the modem ALDB."""

        def create_messages():
            """Send response messages."""
            ack_first_topic = 'ack.{}'.format(GET_FIRST_ALL_LINK_RECORD)
            ack_topic = 'ack.{}'.format(GET_NEXT_ALL_LINK_RECORD)
            nak_topic = 'nak.{}'.format(GET_NEXT_ALL_LINK_RECORD)
            rec_topic = ALL_LINK_RECORD_RESPONSE
            topics = [
                TopicItem(ack_first_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(ack_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(ack_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(ack_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(ack_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(ack_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(ack_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(ack_topic, {}, 1),
                TopicItem(rec_topic, fill_rec(0x2e, 0x01, '010102', 0x02, 0x03, 0x04), 1),
                TopicItem(nak_topic, {}, 1),
                TopicItem(nak_topic, {}, 1),
                TopicItem(nak_topic, {}, 1)]
            return topics

        responses = create_messages()
        send_topics(responses)
        response = await self.aldb.async_load()
        _LOGGER.debug('Done LOAD function.')
        _LOGGER.debug('Status: %s', response.name)
        assert self.aldb.is_loaded
        assert len(self.aldb) == 8

    @async_case
    async def test_empty_aldb(self):
        """Test for an empty ALDB."""

        def create_messages():
            """Send 3 NAK messages."""
            nak_topic = 'nak.{}'.format(GET_FIRST_ALL_LINK_RECORD)
            topics = [TopicItem(nak_topic, {}, 1),
                      TopicItem(nak_topic, {}, 1),
                      TopicItem(nak_topic, {}, 1)]
            return topics

        responses = create_messages()
        send_topics(responses)
        response = await self.aldb.async_load()
        _LOGGER.debug('Done LOAD function.')
        _LOGGER.debug('Status: %s', response.name)
        assert self.aldb.is_loaded


if __name__ == '__main__':
    unittest.main()
