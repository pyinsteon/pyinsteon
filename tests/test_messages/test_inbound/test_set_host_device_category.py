"""Test Set Host Device Category."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, DeviceCategory, MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestSetHostDeviceCategory(unittest.TestCase):
    """Test Set Host Device Category."""

    def setUp(self):
        """Test set up."""
        self.hex = "0266030405"
        self.hex_ack = "026603040506"
        self.message_id = MessageId(0x66)
        self.cat = DeviceCategory(0x03)
        self.subcat = int(0x04)
        self.firmware = int(0x05)
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
