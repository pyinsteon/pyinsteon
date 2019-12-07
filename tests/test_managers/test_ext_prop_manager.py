"""Test extended property management."""
import asyncio
import unittest

from pyinsteon.address import Address
from pyinsteon.managers.get_set_ext_property_manager import (
    GetSetExtendedPropertyManager,
)
from pyinsteon.protocol.commands import EXTENDED_GET_SET
from pyinsteon.utils import build_topic
from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, send_topics


class DataValue:
    def __init__(self):
        self._value = None

    @property
    def value(self):
        return self._value

    def update(self, value):
        self._value = value


class TestExtendedPropertyManager(unittest.TestCase):
    """Text extended property management."""

    def setUp(self):
        self._address = Address("010203")
        self._epm = GetSetExtendedPropertyManager(self._address)
        set_log_levels(logger_topics=True)

    @async_case
    async def test_data_update(self):
        """Test data updates."""
        from pyinsteon import pub
        from pyinsteon.protocol.messages.user_data import UserData

        prop1 = DataValue()
        prop2 = DataValue()
        prop3 = DataValue()
        prop4 = DataValue()
        prop5 = DataValue()
        prop6 = DataValue()
        prop7 = DataValue()
        prop8 = DataValue()
        prop9 = DataValue()
        prop100 = DataValue()
        prop101 = DataValue()
        prop102 = DataValue()
        prop103 = DataValue()

        self._epm.subscribe(prop1, prop1.update, 0, 3, None, None)
        self._epm.subscribe(prop2, prop2.update, 0, 3, None, None)
        self._epm.subscribe(prop3, prop3.update, 0, 3, None, None)
        self._epm.subscribe(prop4, prop4.update, 0, 4, None, None)
        self._epm.subscribe(prop5, prop5.update, 0, 5, None, None)
        self._epm.subscribe(prop6, prop6.update, 0, 6, None, None)
        self._epm.subscribe(prop7, prop7.update, 0, 7, None, None)
        self._epm.subscribe(prop8, prop8.update, 0, 8, None, None)
        self._epm.subscribe(prop9, prop9.update, 0, 9, None, None)
        self._epm.subscribe(prop100, prop100.update, 0, 10, 0, None)
        self._epm.subscribe(prop101, prop101.update, 0, 10, 1, None)
        self._epm.subscribe(prop102, prop102.update, 0, 10, 2, None)
        self._epm.subscribe(prop103, prop103.update, 0, 10, 3, None)

        address = "a1b2b3"
        user_data = UserData(
            {
                "d1": 0x00,
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
            topic=EXTENDED_GET_SET, address=self._address, message_type="direct"
        )

        topic_ack = TopicItem(ack, cmd_kwargs(0x2E, 0x00, None), 1)
        topic_dir_ack = TopicItem(
            dir_ack, cmd_kwargs(0x2E, 0x00, None, target="030405"), 1
        )
        topic_resp = TopicItem(
            resp, cmd_kwargs(0x2E, 0x00, user_data, target="030405"), 0.2
        )
        send_topics([topic_ack, topic_dir_ack, topic_resp])
        result = await self._epm.async_get(group=1)
        assert int(result) == 1
        await asyncio.sleep(1)
        assert prop1.value is None
        assert prop3.value == 0x03
        assert prop101.value
        assert not prop102.value


if __name__ == "__main__":
    unittest.main()
