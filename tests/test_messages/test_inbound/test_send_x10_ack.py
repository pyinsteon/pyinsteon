"""Test X10 commands."""

import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


class TestSendX10(unittest.TestCase):
    """Test the SendX10 command."""

    def setUp(self):
        """Set up the TestSendX10 tests."""
        self.hex = "02630102"
        self.hex_ack = "0263010206"
        self.message_id = MessageId(0x63)
        self.raw_x10 = int(0x01)
        self.x10_flag = int(0x02)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_ack)
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test X10 message ID."""
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        """Test X10 message ACK/NAK."""
        assert self.msg.ack == self.ack

    def test_bytes(self):
        """Test X10 message to bytes."""
        assert bytes(self.msg) == unhexlify(self.hex_ack)
