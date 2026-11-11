"""Test Standard Received."""

import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MessageId
from pyinsteon.data_types.message_flags import MessageFlags
from pyinsteon.protocol.messages.inbound import create
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


class TestHubStandardReceived(TestStandardReceived):
    """Test a standard received message reported by the Hub with id 0x5C."""

    def setUp(self):
        """Test set up."""
        super().setUp()
        self.msg, self.msg_bytes = hex_to_inbound_message("025C010203040506070809")


class TestHubStatusRequestEcho(unittest.TestCase):
    """Test that the Hub's 0x5C echo of a status request is dropped."""

    def test_echo_dropped(self):
        """Test the echo is dropped and the real reply that follows is read."""
        echo = bytearray(unhexlify("025C2942AF4B4193231901"))
        reply = bytearray(unhexlify("02502942AF4B41932117C1"))
        msg, remaining = create(echo + reply)
        assert msg is None
        assert remaining == reply
        msg, remaining = create(remaining)
        assert msg.message_id == MessageId.STANDARD_RECEIVED
        assert msg.cmd1 == 0x17
        assert msg.cmd2 == 0xC1
        assert remaining == bytearray()

    def test_partial_frame_waits(self):
        """Test a partial 0x5C frame is kept until the rest arrives."""
        partial = bytearray(unhexlify("025C2942AF4B41"))
        msg, remaining = create(partial)
        assert msg is None
        assert remaining == partial


if __name__ == "__main__":
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()
