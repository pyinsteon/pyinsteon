"""Test Get Next All-Link Record."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestGetNextAllLinkRecord(unittest.TestCase):
    """Test Get Next All-Link Record."""

    def setUp(self):
        """Set up test."""
        self.hex = "026A"
        self.hex_ack = "026A06"
        self.message_id = MessageId(0x6A)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_ack)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test ID."""
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        """Test ACK/NAK"""
        assert self.msg.ack == self.ack

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == unhexlify(self.hex_ack)
