"""Test Button Event Report."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import ImButtonEvents, MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


class TestButtonEventReport(unittest.TestCase):
    """Test Button Event Report."""

    def setUp(self):
        """Set up the test."""
        self.hex = "025403"
        self.message_id = MessageId(0x54)
        self.event = ImButtonEvents(0x03)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test ID."""
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == unhexlify(self.hex)
