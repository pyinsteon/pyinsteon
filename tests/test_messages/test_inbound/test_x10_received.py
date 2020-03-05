"""Test X10 message receieved."""

import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


class TestX10Received(unittest.TestCase):
    """Test the X10Received message type."""

    def setUp(self):
        """Set up the TextX10Received tests."""
        self.message_id = MessageId(0x52)
        self.hex = "02520380"
        self.raw_x10 = int(0x03)
        self.x10_flag = int(0x04)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test X10 received message ID."""
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        """Test X10 message to bytes."""
        assert bytes(self.msg) == unhexlify(self.hex)


if __name__ == "__main__":
    unittest.main()
