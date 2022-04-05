"""Test sending standard message."""

import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.address import Address
from pyinsteon.constants import MessageId
from pyinsteon.data_types.message_flags import MessageFlags

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import send_standard  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase
from tests.utils import async_case


class TestSendStandard(unittest.TestCase, OutboundBase):
    """Test sending standard message."""

    def setUp(self):
        """Test set up."""
        self.hex = "0262010203040506"
        self.message_id = MessageId.SEND_STANDARD
        self.address = Address("010203")
        self.flags = MessageFlags(0x04)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)

        kwargs = {
            "address": self.address,
            "flags": self.flags,
            "cmd1": self.cmd1,
            "cmd2": self.cmd2,
        }

        super(TestSendStandard, self).base_setup(
            MessageId.SEND_STANDARD, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    @async_case
    async def test_address(self):
        """Test address."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.address == self.address

    @async_case
    async def test_flags(self):
        """Test flags."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.flags == self.flags

    @async_case
    async def test_cmd1(self):
        """Test cmd1."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.cmd1 == self.cmd1

    @async_case
    async def test_cmd2(self):
        """Test cmd2."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.cmd2 == self.cmd2


if __name__ == "__main__":
    unittest.main()
