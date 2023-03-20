"""Test the Thermostat status manager."""
import asyncio
from unittest import TestCase
from unittest.mock import AsyncMock

from pyinsteon.data_types.user_data import UserData
from pyinsteon.managers.thermostat_status_manager import GetThermostatStatus
from pyinsteon.topics import EXTENDED_GET_RESPONSE, EXTENDED_GET_SET

from .. import set_log_levels
from ..utils import TopicItem, async_case, random_address, send_topics


class TestThermostatStatusManager(TestCase):
    """Test the thermostat status manager."""

    def setUp(self) -> None:
        """Set up the tests."""
        set_log_levels(logger_topics=True)

    @async_case
    async def test_status_commands(self):
        """Test the thermostat status commands."""
        status_receved = AsyncMock()
        set_point_received = AsyncMock

        def _status_received(
            day,
            hour,
            minute,
            second,
            system_mode,
            fan_mode,
            cool_set_point,
            humidity,
            temperature,
            cooling,
            heating,
            celsius,
            heat_set_point,
        ):
            nonlocal status_receved
            status_receved = True

        def _set_point_received(
            humidity_high,
            humidity_low,
            firmwire,
            cool_set_point,
            heat_set_point,
            rf_offset,
        ):
            """Receive set point info."""
            nonlocal set_point_received
            set_point_received = True

        address = random_address()
        target = random_address()
        command = GetThermostatStatus(address=address)
        command.subscribe_status(_status_received)
        command.subscribe_set_point(_set_point_received)
        ack_topic = f"ack.{address.id}.{EXTENDED_GET_SET}.direct"
        dir_ack_topic = f"{address.id}.{EXTENDED_GET_SET}.direct_ack"
        response_topic = f"{address.id}.{EXTENDED_GET_RESPONSE}.direct"
        ud_status_ack = UserData()
        ack_status = TopicItem(
            ack_topic, {"cmd1": 0x2E, "cmd2": 0x02, "user_data": ud_status_ack}, 0.2
        )
        dir_ack_status = TopicItem(
            dir_ack_topic,
            {
                "cmd1": 0x2E,
                "cmd2": 0x02,
                "user_data": None,
                "target": target,
                "hops_left": 0,
            },
            0.1,
        )
        user_data_response = UserData(
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
            }
        )
        status_response = TopicItem(
            response_topic,
            {
                "cmd1": 0x2E,
                "cmd2": 0x02,
                "user_data": user_data_response,
                "target": target,
                "hops_left": 0,
            },
            1,
        )

        ud_setpt_ack = UserData()
        ack_setpt = TopicItem(
            ack_topic, {"cmd1": 0x2E, "cmd2": 0x00, "user_data": ud_setpt_ack}, 0.1
        )
        dir_ack_setpt = TopicItem(
            dir_ack_topic,
            {
                "cmd1": 0x2E,
                "cmd2": 0x00,
                "user_data": None,
                "target": target,
                "hops_left": 0,
            },
            0.1,
        )
        ud_setpt_response = UserData(
            {
                "d1": 0x00,
                "d2": 0x01,
                "d3": 0x00,
                "d4": 0x04,
                "d5": 0x05,
                "d6": 0x06,
                "d7": 0x07,
                "d8": 0x08,
                "d9": 0x09,
                "d10": 0x0A,
                "d11": 0x0B,
                "d12": 0x0C,
            }
        )
        setpt_response = TopicItem(
            response_topic,
            {
                "cmd1": 0x2E,
                "cmd2": 0x00,
                "user_data": ud_setpt_response,
                "target": target,
                "hops_left": 0,
            },
            0.1,
        )

        send_topics(
            [
                ack_status,
                dir_ack_status,
                status_response,
                ack_setpt,
                dir_ack_setpt,
                setpt_response,
            ]
        )
        await command.async_status()
        await asyncio.sleep(0.1)
        assert status_receved
        assert set_point_received
