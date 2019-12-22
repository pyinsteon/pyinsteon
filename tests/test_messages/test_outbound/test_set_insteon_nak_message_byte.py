from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import set_nak_message_byte
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSetInsteonNakMessageByte(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "027003"
        self.cmd2 = int(0x03)

        kwargs = {"cmd2": self.cmd2}

        super(TestSetInsteonNakMessageByte, self).base_setup(
            MessageId.SET_NAK_MESSAGE_BYTE, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2


if __name__ == "__main__":
    unittest.main()
