"""Test the Leak Sensor device heartbeat handling."""

import asyncio
from datetime import datetime, timedelta
import unittest

from pyinsteon.address import Address
from pyinsteon.constants import MessageFlagType
from pyinsteon.device_types.security_health_safety import (
    SecurityHealthSafety_LeakSensor,
)
from pyinsteon.topics import OFF, ON
from pyinsteon.utils import build_topic

from .. import set_log_levels
from ..utils import TopicItem, async_case, random_address, send_topics


class TestLeakSensorHeartbeat(unittest.TestCase):
    """Test the Leak Sensor heartbeat group."""

    def setUp(self):
        """Set up the tests."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    async def async_setup(self):
        """Set up the device with a known dry state."""
        self.address = random_address()
        self.device = SecurityHealthSafety_LeakSensor(
            self.address, 0x10, 0x08, 0x00, "Test Leak Sensor", "Model"
        )
        self.dry_group = self.device.groups[self.device.DRY_GROUP]
        self.wet_group = self.device.groups[self.device.WET_GROUP]
        self.hb_group = self.device.groups[self.device.HEARTBEAT_GROUP]
        self.hb_mgr = self.device._managers[self.device.HEARTBEAT_GROUP]
        self.dry_group.value = True
        self.wet_group.value = False

    def _miss_heartbeat(self):
        """Force the heartbeat manager to detect a missed heartbeat."""
        self.hb_mgr._last_heartbeat = datetime.now() - timedelta(
            minutes=self.hb_mgr.max_duration + 1
        )
        self.hb_mgr._check_heartbeat()

    async def _send_heartbeat(self, topic_name, cmd1, cmd2):
        """Send a heartbeat broadcast message from the device."""
        topic = build_topic(
            topic_name,
            None,
            self.address,
            self.device.HEARTBEAT_GROUP,
            MessageFlagType.ALL_LINK_BROADCAST,
        )
        send_topics(
            [
                TopicItem(
                    topic,
                    {
                        "cmd1": cmd1,
                        "cmd2": cmd2,
                        "target": Address("000004"),
                        "user_data": None,
                        "hops_left": 3,
                    },
                    0.05,
                )
            ]
        )
        await asyncio.sleep(0.1)

    def _assert_dry(self):
        assert self.dry_group.value is True
        assert self.wet_group.value is False

    @async_case
    async def test_missed_heartbeat_sets_heartbeat_group(self):
        """Test a missed heartbeat sets group 4 to True without changing wet/dry."""
        await self.async_setup()
        assert not self.hb_group.value

        self._miss_heartbeat()

        assert self.hb_group.value is True
        self._assert_dry()

    @async_case
    async def test_heartbeat_on_clears_missed_heartbeat(self):
        """Test an ON heartbeat returns group 4 to False without changing wet/dry."""
        await self.async_setup()
        self._miss_heartbeat()
        assert self.hb_group.value is True

        await self._send_heartbeat(ON, 0x11, 0xFF)

        assert self.hb_group.value is False
        self._assert_dry()

    @async_case
    async def test_heartbeat_off_clears_missed_heartbeat(self):
        """Test an OFF heartbeat returns group 4 to False without changing wet/dry."""
        await self.async_setup()
        self._miss_heartbeat()
        assert self.hb_group.value is True

        await self._send_heartbeat(OFF, 0x13, 0x00)

        assert self.hb_group.value is False
        self._assert_dry()


if __name__ == "__main__":
    unittest.main()
