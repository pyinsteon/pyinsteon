"""Test sending extended message."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.message_flags import MessageFlags
# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import send_extended
from pyinsteon.protocol.messages.user_data import UserData
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSendExtended(unittest.TestCase, OutboundBase):
    """Test sending extended message."""

    def setUp(self):
        """Test set up."""
        self.hex = "0262010203140506a1a2a3a4a5a6a7a8a9aaabacadae"
        self.message_id = MessageId.SEND_EXTENDED
        self.address = Address("010203")
        self.flags = MessageFlags(0x14)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.user_data = UserData(unhexlify(self.hex)[8:])

        kwargs = {
            "address": self.address,
            "flags": self.flags,
            "cmd1": self.cmd1,
            "cmd2": self.cmd2,
            "user_data": self.user_data,
        }

        super(TestSendExtended, self).base_setup(
            MessageId.SEND_EXTENDED, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_address(self):
        """Test address."""
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


if __name__ == "__main__":
    unittest.main()
