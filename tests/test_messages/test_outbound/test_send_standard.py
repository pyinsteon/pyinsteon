"""Test cases for Cancel All Linking."""
import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import send_standard  # noqa: F401
from pyinsteon.topics import SEND_STANDARD
from tests.test_messages.test_outbound.outbound_base import OutboundBase
from tests.utils import async_case


class TestSendStandard(unittest.TestCase, OutboundBase):
    """Test Cancel All-Linking command."""

    def setUp(self):
        """Set up the TestCancelAllLinking tests."""
        self.hex = "02620102030011ff"
        self.address = Address("010203")
        self.cmd1 = 0x11
        self.cmd2 = 0xFF
        kwargs = {"address": self.address, "cmd1": self.cmd1, "cmd2": self.cmd2}
        super(TestSendStandard, self).base_setup(
            MessageId.SEND_STANDARD, unhexlify(self.hex), **kwargs
        )

    @async_case
    async def test_no_flags(self):
        """Test send standard without flags."""
        pub.sendMessage(f"send.{SEND_STANDARD}", address="010203", cmd1=0x11, cmd2=0xAB)
        assert self.msg.cmd2 == 0xAB


if __name__ == "__main__":
    unittest.main()
