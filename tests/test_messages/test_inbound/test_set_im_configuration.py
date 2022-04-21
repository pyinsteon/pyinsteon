"""Test Set IM Configuration."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import AckNak, MessageId
from pyinsteon.data_types.im_config_flags import IMConfigurationFlags
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestSetImConfiguration(unittest.TestCase):
    """Test Set IM Configuration."""

    def setUp(self):
        """Test set up."""
        self.hex = "026B30"
        self.hex_ack = "026B3006"
        self.message_id = MessageId(0x6B)
        self.flags = IMConfigurationFlags(0x30)
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


if __name__ == "__main__":
    unittest.main()
