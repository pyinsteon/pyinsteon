"""Test the on_level command handler."""

import unittest

from pyinsteon.address import Address
from pyinsteon.constants import ResponseStatus
from pyinsteon.handlers.to_device.on_level import OnLevelCommand
from tests import set_log_levels
from tests.utils import TopicItem, async_case, send_topics


class TestOnLevel(unittest.TestCase):
    """Test the on_level command handler."""

    async def async_setup(self):
        """Set up the test."""
        self._address = Address("aabbcc")
        self.handler1 = OnLevelCommand(self._address, group=1)
        self.handler1.subscribe(self.set_on_level_group_1)
        self.handler2 = OnLevelCommand(self._address, group=2)
        self.handler2.subscribe(self.set_on_level_group_2)
        self.handler3 = OnLevelCommand(self._address, group=3)
        self.handler3.subscribe(self.set_on_level_group_3)
        self._on_level_1 = None
        self._on_level_2 = None
        self._on_level_3 = None

        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    def set_on_level_group_1(self, on_level, group=None):
        """Handle callback to on_level direct_ack."""
        self._on_level_1 = on_level

    def set_on_level_group_2(self, on_level, group=None):
        """Handle callback to on_level direct_ack."""
        self._on_level_2 = on_level

    def set_on_level_group_3(self, on_level, group=None):
        """Handle callback to on_level direct_ack."""
        self._on_level_3 = on_level

    @async_case
    async def test_on_level(self):
        """Test the ON command."""
        await self.async_setup()
        cmd1 = 0x11
        cmd2 = 0xAA
        self._on_level_1 = None
        self._on_level_2 = None
        self._on_level_3 = None

        ack_topic = "ack.{}.{}.on.direct".format(self._address.id, 1)
        direct_ack_topic = "{}.on.direct_ack".format(self._address.id)

        topics = [
            TopicItem(ack_topic, {"cmd1": cmd1, "cmd2": cmd2, "user_data": None}, 0.5),
            TopicItem(
                direct_ack_topic,
                {
                    "cmd1": cmd1,
                    "cmd2": cmd2,
                    "target": "4d5e6f",
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
        ]
        send_topics(topics)
        assert await self.handler1.async_send(on_level=cmd2)
        assert self._on_level_1 == cmd2
        assert self._on_level_2 is None
        assert self._on_level_3 is None

    @async_case
    async def test_on_level_group(self):
        """Test the ON command."""
        await self.async_setup()
        cmd1 = 0x11
        cmd2 = 0xAA
        self._on_level_1 = None
        self._on_level_2 = None
        self._on_level_3 = None

        ack_topic = "ack.{}.{}.on.direct".format(self._address.id, 2)
        direct_ack_topic = "{}.on.direct_ack".format(self._address.id)

        topics = [
            TopicItem(
                ack_topic, {"cmd1": cmd1, "cmd2": cmd2, "user_data": {"d1": 2}}, 0.5
            ),
            TopicItem(
                direct_ack_topic,
                {
                    "cmd1": cmd1,
                    "cmd2": cmd2,
                    "target": "4d5e6f",
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
        ]
        send_topics(topics)
        assert await self.handler2.async_send(on_level=cmd2)
        assert self._on_level_1 is None
        assert self._on_level_2 == cmd2
        assert self._on_level_3 is None

    @async_case
    async def test_on_level_nak(self):
        """Test the ON command."""
        await self.async_setup()
        cmd1 = 0x11
        cmd2 = 0xAA

        ack_topic = "ack.{}.{}.on.direct".format(self._address.id, 3)
        direct_nak_topic = "{}.on.direct_nak".format(self._address.id)

        topics = [
            TopicItem(
                ack_topic, {"cmd1": cmd1, "cmd2": cmd2, "user_data": {"d1": 3}}, 0.5
            ),
            TopicItem(
                direct_nak_topic,
                {
                    "cmd1": cmd1,
                    "cmd2": cmd2,
                    "target": "4d5e6f",
                    "user_data": None,
                    "hops_left": 3,
                },
                0.5,
            ),
        ]
        send_topics(topics)
        response = await self.handler3.async_send(on_level=cmd2)
        assert response == ResponseStatus.UNCLEAR


if __name__ == "__main__":
    unittest.main()
