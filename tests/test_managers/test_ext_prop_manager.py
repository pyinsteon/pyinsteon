"""Test extended property management."""
import asyncio
import unittest

from pyinsteon.address import Address
from pyinsteon.commands import EXTENDED_GET_RESPONSE, EXTENDED_GET_SET
from pyinsteon.managers.get_set_ext_property_manager import (
    GetSetExtendedPropertyManager,
)
from pyinsteon.protocol.messages.user_data import UserData
from pyinsteon.utils import build_topic
from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, send_topics


class DataValue:
    """Data value type."""

    def __init__(self):
        """Init the DataValue class."""
        self._value = None

    @property
    def value(self):
        """Return the value."""
        return self._value

    def update(self, value):
        """Update the value."""
        self._value = value


class TestExtendedPropertyManager(unittest.TestCase):
    """Text extended property management."""

    def setUp(self):
        """Set up the test."""
        self._address = Address("010203")
        self._properties = {}
        self._epm = GetSetExtendedPropertyManager(self._address)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    @async_case
    async def test_data_update(self):
        """Test data updates."""

        self._properties["prop3"] = self._epm.create("prop3", 1, 3, None, None)
        self._properties["prop4"] = self._epm.create("prop4", 1, 4, None, None)
        self._properties["prop5"] = self._epm.create("prop5", 1, 5, None, None)
        self._properties["prop6"] = self._epm.create("prop6", 1, 6, None, None)
        self._properties["prop7"] = self._epm.create("prop7", 1, 7, None, None)
        self._properties["prop8"] = self._epm.create("prop8", 1, 8, None, None)
        self._properties["prop9"] = self._epm.create("prop9", 1, 9, None, None)
        self._properties["prop100"] = self._epm.create("prop100", 1, 10, 0, None)
        self._properties["prop101"] = self._epm.create("prop101", 1, 10, 1, None)
        self._properties["prop102"] = self._epm.create("prop102", 1, 10, 2, None)
        self._properties["prop103"] = self._epm.create("prop103", 1, 10, 3, None)

        user_data = UserData(
            {
                "d1": 0x01,
                "d2": 0x01,
                "d3": 0x03,
                "d4": 0x04,
                "d5": 0x05,
                "d6": 0x06,
                "d7": 0x07,
                "d8": 0x08,
                "d9": 0x09,
                "d10": 0x0A,
                "d11": 0x0B,
                "d12": 0x0C,
                "d13": 0x0D,
                "d14": 0x0E,
            }
        )
        ack = build_topic(
            prefix="ack",
            topic=EXTENDED_GET_SET,
            address=self._address,
            message_type="direct",
        )
        dir_ack = build_topic(
            topic=EXTENDED_GET_SET, address=self._address, message_type="direct_ack"
        )
        resp = build_topic(
            topic=EXTENDED_GET_RESPONSE, address=self._address, message_type="direct"
        )

        topic_ack = TopicItem(
            ack, cmd_kwargs(0x2E, 0x00, UserData({"d1": 1, "d2": 0})), 1
        )
        topic_dir_ack = TopicItem(
            dir_ack, cmd_kwargs(0x2E, 0x00, None, target="030405"), 0.1
        )
        topic_resp = TopicItem(
            resp, cmd_kwargs(0x2E, 0x00, user_data, target="030405"), 0.2
        )
        send_topics([topic_ack, topic_dir_ack, topic_resp])
        result = await self._epm.async_read(group=1)
        assert int(result) == 1
        await asyncio.sleep(1)
        assert self._properties["prop3"].value == 0x03
        assert self._properties["prop9"].value == 0x09
        assert self._properties["prop101"].value
        assert not self._properties["prop102"].value


if __name__ == "__main__":
    unittest.main()
