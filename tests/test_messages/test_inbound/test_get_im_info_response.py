"""Test Get IM Info Response."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import AckNak, DeviceCategory, MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestGetImInfoResponse(unittest.TestCase):
    """Test Get IM Info Response."""

    def setUp(self):
        """Set up test."""
        self.hex = "0260"
        self.hex_ack = "026003040507070806"
        self.message_id = MessageId(0x60)
        self.address = Address("030405")
        self.cat = DeviceCategory(0x07)
        self.subcat = int(0x07)
        self.firmware = int(0x08)
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
