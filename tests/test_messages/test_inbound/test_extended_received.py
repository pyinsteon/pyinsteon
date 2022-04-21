"""Test Extended Received."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.data_types.message_flags import MessageFlags
from pyinsteon.data_types.user_data import UserData
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestExtendedSendAck(unittest.TestCase):
    """Test Extended Received."""

    def setUp(self):
        """Set up the test."""
        self.hex_data = "0251112233445566778899a1a2a3a4a5a6a7a8a9aaabacadae"
        self.message_id = 0x51
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.address = Address("112233")
        self.target = Address("445566")
        self.flags = MessageFlags(0x77)
        self.cmd1 = int(0x88)
        self.cmd2 = int(0x99)
        self.user_data = UserData(unhexlify("a1a2a3a4a5a6a7a8a9aaabacadae"))

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_data)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test id."""
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

    def test_user_data(self):
        """Test user_data."""
        assert self.msg.user_data == self.user_data

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == self.bytes_data

    def test_len(self):
        """Test len."""
        assert len(self.msg) == 25


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()
