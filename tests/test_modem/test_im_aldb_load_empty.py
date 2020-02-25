"""Test loading the IM ALDB."""
import unittest

from pyinsteon.address import Address
from pyinsteon.aldb.modem_aldb import ModemALDB
from pyinsteon.topics import (ALL_LINK_RECORD_RESPONSE,
                              GET_FIRST_ALL_LINK_RECORD,
                              GET_NEXT_ALL_LINK_RECORD)
from tests import _LOGGER, set_log_levels
from tests.utils import TopicItem, async_case, send_topics


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


class TestModemALDBLoadEmpty(unittest.TestCase):
    """Test the ModemALDB class."""

    def setUp(self):
        """Setup the test."""
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        _LOGGER.debug("Running setUp")
        self.aldb = ModemALDB("010101")

    @async_case
    async def test_empty_aldb(self):
        """Test for an empty ALDB."""

        def create_messages():
            """Send 3 NAK messages."""
            nak_topic = "nak.{}".format(GET_FIRST_ALL_LINK_RECORD)
            topics = [
                TopicItem(nak_topic, {}, 1),
                TopicItem(nak_topic, {}, 1),
                TopicItem(nak_topic, {}, 1),
            ]
            return topics

        responses = create_messages()
        send_topics(responses)
        response = await self.aldb.async_load()
        _LOGGER.debug("Done LOAD function.")
        _LOGGER.debug("Status: %s", response.name)
        assert self.aldb.is_loaded


if __name__ == "__main__":
    unittest.main()
