"""Test the on_level command handler."""
import asyncio
import unittest
from pyinsteon.handlers.on_level import OnLevelCommand
from tests.utils import async_case, async_send_topics, TopicItem
from pyinsteon.constants import ResponseStatus


class TestOnLevel(unittest.TestCase):
    """Test the on_level command handler."""

    def setUp(self):
        """Set up the test."""
        self._address = '1a2b3c'
        self.handler = OnLevelCommand(self._address)
        self.handler.subscribe(self.set_on_level)
        self._on_level = None
        self._group = None
        self.ack_topic = 'ack.{}.on.direct'.format(self._address)
        self.direct_ack_topic = '{}.on.direct_ack'.format(self._address)
        self.direct_nak_topic = '{}.on.direct_nak'.format(self._address)

    def set_on_level(self, on_level, group):
        """Callback to on_level direct_ack."""
        self._on_level = on_level
        self._group = group

    @async_case
    async def test_on_level(self):
        """Test the ON command."""
        cmd2 = 0xaa
        topics = [TopicItem(self.ack_topic,
                            {"cmd2": cmd2, "target": '4d5e6f', "user_data": None}, .5),
                  TopicItem(self.direct_ack_topic,
                            {"cmd2": cmd2, "target": '4d5e6f', "user_data": None}, .5)]
        asyncio.ensure_future(async_send_topics(topics))
        assert await self.handler.async_send(on_level=cmd2)
        assert self._on_level == cmd2

    @async_case
    async def test_on_level_group(self):
        """Test the ON command."""
        cmd2 = 0xaa
        group = 0x02
        topics = [TopicItem(self.ack_topic,
                            {"cmd2": cmd2, "target": '4d5e6f', "user_data": {'d1': group}}, .5),
                  TopicItem(self.direct_ack_topic,
                            {"cmd2": cmd2, "target": '4d5e6f', "user_data":  {'d1': group}}, .5)]
        asyncio.ensure_future(async_send_topics(topics))
        assert await self.handler.async_send(on_level=cmd2)
        assert self._on_level == cmd2
        assert self._group == group

    @async_case
    async def test_on_level_nak(self):
        """Test the ON command."""
        cmd2 = 0xaa
        group = 0x02
        topics = [TopicItem(self.ack_topic,
                            {"cmd2": cmd2, "target": '4d5e6f', "user_data": {'d1': group}}, .5),
                  TopicItem(self.direct_nak_topic,
                            {"cmd2": cmd2, "target": '4d5e6f', "user_data":  {'d1': group}}, .5)]
        asyncio.ensure_future(async_send_topics(topics))
        assert await self.handler.async_send(on_level=cmd2)  == ResponseStatus.UNCLEAR

if __name__ == '__main__':
    unittest.main()
