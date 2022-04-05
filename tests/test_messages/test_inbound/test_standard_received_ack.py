"""Test Standard Received."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.data_types.message_flags import MessageFlags
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestStandardReceived(unittest.TestCase):
    """Test Standard Received."""

    def setUp(self):
        """Test set up."""
        self.hex_data = "0250010203040506070809"
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.message_id = 0x50
        self.address = Address("010203")
        self.target = Address("040506")
        self.flags = MessageFlags(0x07)
        self.cmd1 = int(0x08)
        self.cmd2 = int(0x09)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_data)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test ID."""
        assert self.msg.message_id == self.message_id

    def test_address(self):
        """Test address."""
        assert self.msg.address == self.address

    def test_target(self):
        """Test target."""
        assert self.msg.target == self.target

    def test_flags(self):
        """Test flags."""
        assert self.msg.flags == self.flags

    def test_cmd1(self):
        """Test cmd1."""
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        """Test cmd2."""
        assert self.msg.cmd2 == self.cmd2

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == self.bytes_data

    def test_len(self):
        """Test len."""
        assert len(self.msg) == 11


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()
