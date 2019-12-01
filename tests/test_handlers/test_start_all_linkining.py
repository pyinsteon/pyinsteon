"""Test the Start All Linking command handler."""
import unittest
from pyinsteon import pub
from pyinsteon.handlers.start_all_linking import StartAllLinkingCommandHandler
from pyinsteon.constants import AllLinkMode
from pyinsteon.topics import START_ALL_LINKING
from tests.utils import send_topics, TopicItem, async_case


class TestSendAllLinkingCommandHandler(unittest.TestCase):
    """Test the SendAllLink command handler."""

    def setUp(self):
        """Setup the test."""
        self.ack_message = 'ack.{}'.format(START_ALL_LINKING)
        self.handler = StartAllLinkingCommandHandler()
        self.received = False
        pub.subscribe(self.send_listener, START_ALL_LINKING)
        self._sent = False

    @async_case
    async def test_async_send(self):
        """Test the async_send method."""
        topics = [TopicItem(self.ack_message, {"mode": AllLinkMode.CONTROLLER, "group": 0x01}, .5 )]
        send_topics(topics)
        assert await self.handler.async_send(mode=AllLinkMode.CONTROLLER, group=0x01)

    def send_listener(self, mode, group):
        """Subscribe to the send_all_link_command topic."""
        self._sent = True


if __name__ == '__main__':
    unittest.main()
