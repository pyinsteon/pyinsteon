"""Test the Start All Linking command handler."""
import unittest

from pyinsteon import pub
from pyinsteon.constants import AllLinkMode
from pyinsteon.handlers.start_all_linking import StartAllLinkingCommandHandler
from pyinsteon.topics import START_ALL_LINKING
from tests.utils import TopicItem, async_case, send_topics


class TestSendAllLinkingCommandHandler(unittest.TestCase):
    """Test the SendAllLink command handler."""

    def setUp(self):
        """Set up the test."""
        self.ack_message = "ack.{}".format(START_ALL_LINKING)
        self.handler = StartAllLinkingCommandHandler()
        self.received = False
        pub.subscribe(self.send_listener, START_ALL_LINKING)
        self._sent = False

    @async_case
    async def test_async_send(self):
        """Test the async_send method."""
        topics = [
            TopicItem(
                self.ack_message, {"mode": AllLinkMode.CONTROLLER, "group": 0x01}, 0.5
            )
        ]
        send_topics(topics)
        assert await self.handler.async_send(mode=AllLinkMode.CONTROLLER, group=0x01)

    def send_listener(self, mode, group):
        """Subscribe to the start_all_linking topic."""
        self._sent = True


if __name__ == "__main__":
    unittest.main()
