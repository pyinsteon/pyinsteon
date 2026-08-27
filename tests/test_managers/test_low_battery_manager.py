"""Test the low battery manager."""

import asyncio
import unittest

from pyinsteon.address import Address
from pyinsteon.constants import MessageFlagType
import pyinsteon.managers.low_batter_manager
from pyinsteon.topics import OFF, ON
from pyinsteon.utils import build_topic

from tests import set_log_levels
from tests.utils import TopicItem, async_case, random_address, send_topics


class TestLowBatteryManager(unittest.TestCase):
    """Test the low battery manager."""

    async def async_setup(self):
        """Set up the test."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        self._address = random_address()
        self._group = 3
        self._manager = pyinsteon.managers.low_batter_manager.LowBatteryManager(
            self._address, self._group
        )
        self._state_values = []
        self._low_battery_events = []
        self._clear_events = []
        self._manager.subscribe(self.state_value)
        self._manager.subscribe_low_battery_event(self.low_battery_event)
        self._manager.subscribe_low_battery_clear_event(self.clear_event)
        self._on_topic = build_topic(
            ON, None, self._address, self._group, MessageFlagType.ALL_LINK_BROADCAST
        )
        self._off_topic = build_topic(
            OFF, None, self._address, self._group, MessageFlagType.ALL_LINK_BROADCAST
        )
        self._other_topic = build_topic(
            ON, None, self._address, 1, MessageFlagType.ALL_LINK_BROADCAST
        )

    def state_value(self, low_battery):
        """Receive the low battery state."""
        self._state_values.append(low_battery)

    def low_battery_event(self, low_battery):
        """Receive a low battery event."""
        self._low_battery_events.append(low_battery)

    def clear_event(self, low_battery):
        """Receive a low battery clear event."""
        self._clear_events.append(low_battery)

    def _on_item(self, topic, group):
        """Create an ON broadcast topic item."""
        return TopicItem(
            topic,
            {
                "cmd1": 0x11,
                "cmd2": 0x00,
                "target": Address(f"0000{group:02d}"),
                "user_data": None,
                "hops_left": 3,
            },
            0.02,
        )

    def _off_item(self):
        """Create an OFF broadcast topic item."""
        return TopicItem(
            self._off_topic,
            {
                "cmd1": 0x13,
                "cmd2": 0x00,
                "target": Address(f"0000{self._group:02d}"),
                "user_data": None,
                "hops_left": 3,
            },
            0.02,
        )

    @async_case
    async def test_low_battery_on(self):
        """Test a group 3 ON broadcast sets low battery."""
        await self.async_setup()
        send_topics([self._on_item(self._on_topic, self._group)])
        await asyncio.sleep(0.1)
        assert self._low_battery_events == [True]
        assert self._state_values == [True]
        assert not self._clear_events

    @async_case
    async def test_good_battery_off_clears_low_battery(self):
        """Test a group 3 OFF broadcast clears low battery."""
        await self.async_setup()
        send_topics([self._on_item(self._on_topic, self._group)])
        await asyncio.sleep(0.1)
        send_topics([self._off_item()])
        await asyncio.sleep(0.1)
        assert self._low_battery_events == [True]
        assert self._clear_events == [False]
        assert self._state_values == [True, False]

    @async_case
    async def test_unrelated_device_traffic_does_not_clear(self):
        """Test messages from other groups do not clear low battery."""
        await self.async_setup()
        send_topics([self._on_item(self._on_topic, self._group)])
        await asyncio.sleep(0.1)
        send_topics([self._on_item(self._other_topic, 1)])
        await asyncio.sleep(0.3)
        send_topics([self._on_item(self._other_topic, 1)])
        await asyncio.sleep(0.3)
        assert self._low_battery_events == [True]
        assert not self._clear_events
        assert self._state_values == [True]


if __name__ == "__main__":
    unittest.main()
