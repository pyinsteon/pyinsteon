"""Test the SendAllLink command handler."""
import unittest

from pyinsteon import pub
from pyinsteon.handlers.send_all_link import SendAllLinkCommandHandler
from tests.utils import TopicItem, async_case, send_topics


class TestSendAllLinkingCommandHandler(unittest.TestCase):
    """Test the SendAllLink command handler."""

    def setUp(self):
        """Set up the test."""
        self.ack_message = "ack.send_all_link_command"
        self.handler = SendAllLinkCommandHandler()
        self.received = False
        pub.subscribe(self.send_listener, "send_all_link_command")
        self._sent = False

    @async_case
    async def test_async_send(self):
        """Test the async_send method."""
        topics = [
            TopicItem(
                "ack.send_all_link_command",
                {"group": 0x01, "cmd1": 0x11, "cmd2": 0x00},
                0.5,
            )
        ]
        send_topics(topics)
        assert await self.handler.async_send(group=0x01, cmd1=0x11, cmd2=0x00)

    def send_listener(self, group, cmd1, cmd2):
        """Subscribe to the send_all_link_command topic."""
        self._sent = True


if __name__ == "__main__":
    unittest.main()
