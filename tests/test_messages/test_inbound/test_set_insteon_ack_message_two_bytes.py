"""Test Set Insteon ACK Message Two Bytes."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestSetInsteonAckMessageTwoBytes(unittest.TestCase):
    """Test Set Insteon ACK Message Two Bytes."""

    def setUp(self):
        """Test set up."""
        self.hex = "02710304"
        self.hex_ack = "0271030406"
        self.message_id = MessageId(0x71)
        self.cmd1 = int(0x03)
        self.cmd2 = int(0x04)
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
        """Test ACK/NAK."""
        assert self.msg.ack == self.ack

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == unhexlify(self.hex_ack)
