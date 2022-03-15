"""Test the SendAllLink command handler."""
import unittest

from pyinsteon import pub
from pyinsteon.constants import ResponseStatus
from pyinsteon.handlers.send_all_link import SendAllLinkCommandHandler
from tests import set_log_levels
from tests.utils import TopicItem, async_case, send_topics


class TestSendAllLinkingCommandHandler(unittest.TestCase):
    """Test the SendAllLink command handler."""

    def setUp(self):
        """Set up the test."""
        self.ack_message = "ack.send_all_link_command"
        self.received = False
        pub.subscribe(self.send_listener, "send_all_link_command")
        self._sent = False
        set_log_levels(logger_topics=True)

    @async_case
    async def test_async_send(self):
        """Test the async_send method."""
        self.handler = SendAllLinkCommandHandler()
        topics = [
            TopicItem(
                "ack.send_all_link_command",
                {"group": 0x01, "cmd1": 0x11, "cmd2": 0x00},
                0.5,
            )
        ]
        send_topics(topics)
        response = await self.handler.async_send(group=0x01, cmd1=0x11, cmd2=0x00)
        assert response == ResponseStatus.SUCCESS

    def send_listener(self, group, cmd1, cmd2):
        """Subscribe to the send_all_link_command topic."""
        self._sent = True


if __name__ == "__main__":
    unittest.main()
