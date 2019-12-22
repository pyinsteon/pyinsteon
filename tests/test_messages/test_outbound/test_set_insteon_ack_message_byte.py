from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import set_ack_message_byte
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSetInsteonAckMessageByte(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "026803"
        self.message_id = MessageId.SET_ACK_MESSAGE_BYTE
        self.cmd2 = int(0x03)

        kwargs = {"cmd2": self.cmd2}

        super(TestSetInsteonAckMessageByte, self).base_setup(
            self.message_id, unhexlify(self.hex), **kwargs
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
