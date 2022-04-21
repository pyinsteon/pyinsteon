"""Test Get IM Configuration."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, MessageId
from pyinsteon.data_types.im_config_flags import IMConfigurationFlags
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestGetImConfiguration(unittest.TestCase):
    """Test Get IM Configuration."""

    def setUp(self):
        """Set up test."""
        self.hex = "0273"
        self.hex_ack = "027330040506"
        self.message_id = MessageId(0x73)
        self.flags = IMConfigurationFlags(0x30)
        self.spare1 = int(0x04)
        self.spare2 = int(0x05)
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
