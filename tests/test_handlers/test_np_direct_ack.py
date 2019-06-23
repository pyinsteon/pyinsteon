"""Test the on_level command handler."""
import asyncio
import unittest
from pyinsteon.handlers.to_device.on_level import OnLevelCommand
from tests.utils import async_case, send_topics, TopicItem
from pyinsteon.constants import ResponseStatus


class TestNoDirectAck(unittest.TestCase):
    """Test the on_level command handler."""

    def setUp(self):
        """Set up the test."""
        self._address = '1a2b3c'
        self.handler = OnLevelCommand(self._address)
        self.handler.subscribe(self.set_on_level)
        self._on_level = None
        self._group = None
        self.ack_topic = 'ack.{}.on.direct'.format(self._address)

    def set_on_level(self, on_level, group):
        """Callback to on_level direct_ack."""
        self._on_level = on_level
        self._group = group

    @async_case
    async def test_no_direct_ack(self):
        """Test no direct ACK received."""
        cmd1 = 0x99
        cmd2 = 0xaa
        topics = [TopicItem(self.ack_topic,
                            {'cmd1': cmd1, 'cmd2': cmd2, "target": '4d5e6f', "user_data": None}, .5)]
        send_topics(topics)
        assert await self.handler.async_send(on_level=cmd2) == ResponseStatus.FAILURE
        assert self._on_level is None


if __name__ == '__main__':
    unittest.main()
