"""Test the SendAllLink command handler."""
import asyncio
import unittest
from pyinsteon import pub
from pyinsteon.handlers.send_all_link import SendAllLinkingCommandHandler
from tests.utils import async_case, send_topics, TopicItem


class TestSendAllLinkingCommandHandler(unittest.TestCase):
    """Test the SendAllLink command handler."""

    def setUp(self):
        """Setup the test."""
        self.ack_message = "ack.send_all_link_command"
        self.handler = SendAllLinkingCommandHandler()
        self.received = False
        pub.subscribe(self.send_listener, "send_all_link_command")
        self._sent = False

    @async_case
    async def test_async_send(self):
        """Test the async_send method."""
        topics = [
            TopicItem("ack.send_all_link_command", {"group": 0x01, "mode": 0x01}, 0.5)
        ]
        send_topics(topics)
        assert await self.handler.async_send()

    def send_listener(self, group, mode):
        """Subscribe to the send_all_link_command topic."""
        self._sent = True


if __name__ == "__main__":
    unittest.main()
