"""Test Standard Send ACK."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MESSAGE_NAK, MessageId
from pyinsteon.data_types.message_flags import MessageFlags
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


# pylint: disable=no-member
class TestStandardSendAck(unittest.TestCase):
    """Test Standard Send ACK."""

    def setUp(self):
        """Set up test."""
        self.buffer = False
        self.hex_data = "026201020304050615"
        self.bytes_data = unhexlify(self.hex_data)
        self.message_id = MessageId.SEND_STANDARD.value
        self.address = Address("010203")
        self.flags = MessageFlags(0x04)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.ack = MESSAGE_NAK

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

    def test_ack(self):
        """Test ACK."""
        assert self.msg.ack == self.ack

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == self.bytes_data

    def test_len(self):
        """Test len."""
        assert len(self.msg) == 9


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main(buffer=False)
