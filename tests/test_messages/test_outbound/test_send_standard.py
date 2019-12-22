"""Test sending standard message."""

import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.message_flags import MessageFlags

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import send_standard
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSendStandard(unittest.TestCase, OutboundBase):
    def setUp(self):
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
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_address(self):
        assert self.msg.address == self.address

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2


if __name__ == "__main__":
    unittest.main()
