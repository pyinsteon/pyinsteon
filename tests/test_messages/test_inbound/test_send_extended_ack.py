"""Test Extended Send ACK."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MESSAGE_ACK, MessageId
from pyinsteon.data_types.message_flags import MessageFlags
from pyinsteon.data_types.user_data import UserData
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestExtendedSendAck(unittest.TestCase):
    """Test Extended Send ACK."""

    def setUp(self):
        """Test set up."""
        self.buffer = True
        self.hex_data = "0262010203140506a1a2a3a4a5a6a7a8a9aaabacadae06"
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.message_id = MessageId.SEND_EXTENDED.value
        self.address = Address("010203")
        self.flags = MessageFlags(0x14)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.user_data = UserData(unhexlify("a1a2a3a4a5a6a7a8a9aaabacadae"))
        self.ack = MESSAGE_ACK

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
        """Test Address."""
        assert self.msg.address == self.address

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

    def test_ack(self):
        """Test ACK/NAK."""
        assert self.msg.ack == self.ack

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == self.bytes_data

    def test_len(self):
        """Test len."""
        assert len(self.msg) == 23


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()
