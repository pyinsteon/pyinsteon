"""Test X10 devices."""
import asyncio
import unittest

from pyinsteon.constants import (
    HC_LOOKUP,
    UC_LOOKUP,
    ResponseStatus,
    X10Commands,
    X10CommandType,
)
from pyinsteon.device_types import X10Dimmable, X10OnOff, X10OnOffSensor
from pyinsteon.topics import X10_RECEIVED, X10_SEND
from tests import set_log_levels
from tests.utils import TopicItem, async_case, send_topics


class TestX10Devices(unittest.TestCase):
    """Test X10 devices."""

    @async_case
    async def test_x10_sensor(self):
        """Test X10 Sensor device."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        device = X10OnOffSensor("a", 1)
        hc_uc = (HC_LOOKUP["a"] << 4) + UC_LOOKUP[1]
        uc_msg = {"raw_x10": hc_uc, "x10_flag": X10CommandType.UNITCODE}
        hc_cmd = (HC_LOOKUP["a"] << 4) + int(X10Commands.ON)
        cmd_msg = {"raw_x10": hc_cmd, "x10_flag": X10CommandType.COMMAND}

        msgs = [
            TopicItem(X10_RECEIVED, uc_msg, 0.1),
            TopicItem(X10_RECEIVED, cmd_msg, 0.1),
        ]

        send_topics(msgs)
        await asyncio.sleep(1)
        assert device.groups[1].value == 0xFF

    @async_case
    async def test_x10_on_off(self):
        """Test X10 On Off device."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        device = X10OnOff("b", 2)
        ack = "ack.{}".format(X10_SEND)
        hc_uc = (HC_LOOKUP["b"] << 4) + UC_LOOKUP[2]
        uc_msg = {"raw_x10": hc_uc, "x10_flag": X10CommandType.UNITCODE}
        hc_cmd = (HC_LOOKUP["b"] << 4) + X10Commands.ON
        cmd_msg = {"raw_x10": hc_cmd, "x10_flag": X10CommandType.COMMAND}

        msgs = [
            TopicItem(ack, uc_msg, 0.1),
            TopicItem(ack, cmd_msg, 0.1),
        ]

        send_topics(msgs)
        result = await device.async_on()
        assert result == ResponseStatus.SUCCESS
        assert device.groups[1].value == 0xFF

    @async_case
    async def test_x10_dimmable(self):
        """Test X10 Dimmable device."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        device = X10Dimmable("c", 3)
        ack = "ack.{}".format(X10_SEND)
        hc_uc = bytes(bytearray([HC_LOOKUP["c"], UC_LOOKUP[3]]))
        uc_msg = {"raw_x10": hc_uc, "x10_flag": X10CommandType.UNITCODE}
        hc_cmd = bytes(bytearray([HC_LOOKUP["c"], int(X10Commands.BRIGHT)]))
        cmd_msg = {"raw_x10": hc_cmd, "x10_flag": X10CommandType.COMMAND}

        msgs = [
            TopicItem(ack, uc_msg, 0.1),
            TopicItem(ack, cmd_msg, 0.1),
            TopicItem(ack, uc_msg, 0.1),
            TopicItem(ack, cmd_msg, 0.1),
            TopicItem(ack, uc_msg, 0.1),
            TopicItem(ack, cmd_msg, 0.1),
            TopicItem(ack, uc_msg, 0.1),
            TopicItem(ack, cmd_msg, 0.1),
        ]

        send_topics(msgs)
        result = await device.async_on(on_level=45)
        assert result == ResponseStatus.SUCCESS
        assert device.groups[1].value == 44
