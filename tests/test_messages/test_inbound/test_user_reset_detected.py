"""Tesst User Reset Detected."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


class TestUserResetDetected(unittest.TestCase):
    """Tesst User Reset Detected."""

    def setUp(self):
        """Test set up."""
        self.hex = "0255"
        self.message_id = MessageId(0x55)

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
