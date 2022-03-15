"""Test the heartbeat manager."""
import asyncio
import unittest

import pyinsteon.managers.heartbeat_manager
from pyinsteon.address import Address
from pyinsteon.constants import MessageFlagType
from pyinsteon.topics import OFF, ON
from pyinsteon.utils import build_topic
from tests import set_log_levels
from tests.utils import TopicItem, async_case, random_address, send_topics

HB_CHECK_BUFFER = 0


class TestHeartbeatManager(unittest.TestCase):
    """Test the heartbeat manager."""

    async def async_setup(self):
        """Set up the test."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )
        self._address = random_address()
        self._group = 4
        self._hb_mgr = pyinsteon.managers.heartbeat_manager.HeartbeatManager(
            self._address, self._group
        )
        self._heartbeat = None
        self._heartbeat_on = None
        self._heartbeat_off = None
        self._hb_mgr.subscribe(self.heartbeat)
        self._hb_mgr.subscribe_on(self.heartbeat_on)
        self._hb_mgr.subscribe_off(self.heartbeat_off)
        self._on_topic = build_topic(
            ON, None, self._address, self._group, MessageFlagType.ALL_LINK_BROADCAST
        )
        self._off_topic = build_topic(
            OFF, None, self._address, self._group, MessageFlagType.ALL_LINK_BROADCAST
        )

    def heartbeat(self, heartbeat):
        """Receive heartbeat status."""
        self._heartbeat = heartbeat

    def heartbeat_on(self, on_level):
        """Receive heartbeat on message."""
        self._heartbeat_on = on_level

    def heartbeat_off(self, on_level):
        """Receive heartbeat on message."""
        self._heartbeat_off = on_level

    @async_case
    async def test_hb_on(self):
        """Test the heartbeat on message."""
        await self.async_setup()
        on = TopicItem(
            self._on_topic,
            {
                "cmd1": 0x11,
                "cmd2": 0xFF,
                "target": Address("000004"),
                "user_data": None,
                "hops_left": 3,
            },
            0.05,
        )
        send_topics([on])
        await asyncio.sleep(0.1)
        assert not self._heartbeat
        assert self._heartbeat_on
        assert self._heartbeat_off is None

    @async_case
    async def test_hb_off(self):
        """Test the heartbeat on message."""
        await self.async_setup()
        off = TopicItem(
            self._off_topic,
            {
                "cmd1": 0x13,
                "cmd2": 0x00,
                "target": Address("000004"),
                "user_data": None,
                "hops_left": 3,
            },
            0.05,
        )
        send_topics([off])
        await asyncio.sleep(0.1)
        assert not self._heartbeat
        assert not self._heartbeat_off
        assert self._heartbeat_on is None

    @async_case
    async def test_no_hb(self):
        """Test no heartbeat received."""
        await self.async_setup()
        pyinsteon.managers.heartbeat_manager.HB_CHECK_BUFFER = 1
        self._hb_mgr = pyinsteon.managers.heartbeat_manager.HeartbeatManager(
            self._address, self._group, 0
        )
        await asyncio.sleep(1.1)
        assert self._heartbeat


if __name__ == "__main__":
    unittest.main()
