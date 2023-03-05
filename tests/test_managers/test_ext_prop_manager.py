"""Test extended property management."""
# 46, 83, 86, 90-95, 102-110, 125-126, 130-137, 143-159, 164, 166, 168, 176-182, 199-206
import asyncio
from functools import partial
from random import randint
from typing import Dict, Tuple
import unittest

from pyinsteon.address import Address
from pyinsteon.commands import EXTENDED_GET_RESPONSE, EXTENDED_GET_SET
from pyinsteon.config.extended_property import ExtendedProperty
from pyinsteon.data_types.user_data import UserData
from pyinsteon.managers.get_set_ext_property_manager import (
    GetSetExtendedPropertyManager,
)
from pyinsteon.utils import build_topic, set_bit, subscribe_topic, unsubscribe_topic

from tests import set_log_levels
from tests.utils import TopicItem, async_case, cmd_kwargs, random_address, send_topics


def _assert_test(check_vals, data_vals):
    index = 0
    for val in check_vals:
        assert val == data_vals[index]
        index += 1


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


def set_up_env() -> (
    Tuple[
        Address,
        GetSetExtendedPropertyManager,
        Dict[str, ExtendedProperty],
    ]
):
    """Set up the environment."""

    address = random_address()
    ext_prop_mgr = GetSetExtendedPropertyManager(address)
    properties = {}
    properties["prop3"] = ext_prop_mgr.create("prop3", 1, 3, None, 4, update_field=3)
    properties["prop4"] = ext_prop_mgr.create("prop4", 1, 4, None, 4, update_field=4)
    properties["prop5"] = ext_prop_mgr.create("prop5", 1, 5, None, 5)
    properties["prop6"] = ext_prop_mgr.create("prop6", 1, 6, None, None)
    properties["prop7"] = ext_prop_mgr.create("prop7", 1, 7, None, None)
    properties["prop8"] = ext_prop_mgr.create("prop8", 1, 8, None, None)
    properties["prop9"] = ext_prop_mgr.create("prop9", 1, 9, None, 6, update_field=3)
    properties["prop100"] = ext_prop_mgr.create("prop100", 1, 10, 0, 6, update_field=5)
    properties["prop101"] = ext_prop_mgr.create("prop101", 1, 10, 1, 6, update_field=5)
    properties["prop102"] = ext_prop_mgr.create("prop102", 1, 10, 2, 6, update_field=5)
    properties["prop103"] = ext_prop_mgr.create("prop103", 1, 10, 3, 6, update_field=5)

    return address, ext_prop_mgr, properties


class TestExtendedPropertyManager(unittest.TestCase):
    """Text extended property management."""

    def setUp(self):
        """Set up the test."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    @async_case
    async def test_data_update(self):
        """Test data updates."""
        address, ext_prop_mgr, properties = set_up_env()

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
            address=address,
            message_type="direct",
        )
        dir_ack = build_topic(
            topic=EXTENDED_GET_SET, address=address, message_type="direct_ack"
        )
        resp = build_topic(
            topic=EXTENDED_GET_RESPONSE, address=address, message_type="direct"
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
        result = await ext_prop_mgr.async_read(group=1)
        assert int(result) == 1
        await asyncio.sleep(1)
        assert properties["prop3"].value == 0x03
        assert properties["prop9"].value == 0x09
        assert properties["prop101"].value
        assert not properties["prop102"].value

    @async_case
    async def test_writing(self):
        """Test writing properties."""
        _, ext_prop_mgr, properties = set_up_env()
        assert_tests = []

        async def respond_to_send(
            address,
            data1,
            priority=5,
            data2=None,
            data3=None,
            data4=None,
            data5=None,
            data6=None,
            data7=None,
            data8=None,
            data9=None,
            data10=None,
            data11=None,
            data12=None,
            data13=None,
            data14=None,
            crc=None,
        ):
            if assert_tests:
                assert_tests[0](
                    [
                        data2,
                        data3,
                        data4,
                        data5,
                        data6,
                        data7,
                        data8,
                        data9,
                        data10,
                        data11,
                        data12,
                        data13,
                        data14,
                    ]
                )
                assert_tests.pop(0)
            ack_topic = f"ack.{address.id}.extended_get_set.direct"
            direct_ack_topic = f"{address.id}.extended_get_set.direct_ack"
            user_data = UserData(
                bytearray(
                    [
                        data1,
                        data2,
                        data3,
                        data4,
                        data5,
                        data6,
                        data7,
                        data8,
                        data9,
                        data10,
                        data11,
                        data12,
                        data13,
                        data14,
                    ]
                )
            )
            ack_ti = TopicItem(
                ack_topic, {"cmd1": 0x2E, "cmd2": 0x00, "user_data": user_data}, 0
            )
            dir_ti = TopicItem(
                direct_ack_topic,
                {
                    "cmd1": 0x2E,
                    "cmd2": 0x00,
                    "target": random_address(),
                    "hops_left": 0,
                    "user_data": None,
                },
                0.2,
            )
            send_topics([ack_ti, dir_ti])

        prop3_val = randint(0, 100)
        prop4_val = randint(0, 100)
        prop5_val = randint(0, 100)
        prop9_val = randint(0, 100)
        prop100_val = bool(randint(0, 1))
        prop101_val = bool(randint(0, 1))
        prop102_val = bool(randint(0, 1))
        prop103_val = bool(randint(0, 1))
        properties["prop3"].set_value(prop3_val + randint(1, 100))
        properties["prop4"].set_value(prop4_val + randint(1, 100))
        properties["prop5"].set_value(prop5_val + randint(1, 100))
        properties["prop9"].set_value(prop9_val + randint(1, 100))
        properties["prop100"].set_value(not prop100_val)
        properties["prop101"].set_value(not prop101_val)
        properties["prop102"].set_value(not prop102_val)
        properties["prop103"].set_value(not prop103_val)

        send_topic = "send.extended_get_set.direct"
        subscribe_topic(respond_to_send, send_topic)

        # Test writing both set_cmd 4 & 5
        properties["prop3"].new_value = prop3_val
        properties["prop4"].new_value = prop4_val
        properties["prop5"].new_value = prop5_val
        assert_test_1 = partial(_assert_test, [4, prop3_val, prop4_val])
        assert_test_2 = partial(_assert_test, [5, prop5_val])
        assert_tests.append(assert_test_1)
        assert_tests.append(assert_test_2)
        await ext_prop_mgr.async_write()
        assert properties["prop3"].value == prop3_val
        assert properties["prop4"].value == prop4_val
        assert properties["prop5"].value == prop5_val

        # Test writing set_cmd 6
        properties["prop9"].new_value = prop9_val
        properties["prop100"].new_value = prop100_val
        properties["prop101"].new_value = prop101_val
        properties["prop102"].new_value = prop102_val
        properties["prop103"].new_value = prop103_val
        bits_val = 0x00
        bits_val = set_bit(bits_val, 0, prop100_val)
        bits_val = set_bit(bits_val, 1, prop101_val)
        bits_val = set_bit(bits_val, 2, prop102_val)
        bits_val = set_bit(bits_val, 3, prop103_val)
        assert_test_3 = partial(_assert_test, [6, prop9_val, 0, bits_val])
        assert_tests.append(assert_test_3)
        await ext_prop_mgr.async_write()
        assert properties["prop9"].value == prop9_val
        assert properties["prop100"].value == prop100_val
        assert properties["prop101"].value == prop101_val
        assert properties["prop102"].value == prop102_val
        assert properties["prop103"].value == prop103_val

        unsubscribe_topic(respond_to_send, send_topic)


if __name__ == "__main__":
    unittest.main()
