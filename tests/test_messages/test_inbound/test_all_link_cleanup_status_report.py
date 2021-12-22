"""Test All-Link Cleanup Status Report."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestAllLinkCleanupStatusReport(unittest.TestCase):
    """Test All-Link Cleanup Status Report."""

    def setUp(self):
        """Set up test."""
        self.hex = "025806"
        self.message_id = MessageId(0x58)
        self.ack = AckNak(0x06)

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

    def test_ack_nak(self):
        """Test ACK."""
        assert self.msg.ack == self.ack

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == unhexlify(self.hex)


if __name__ == "__main__":
    unittest.main()
