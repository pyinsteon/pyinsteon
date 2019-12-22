from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.outbound import set_ack_message_two_bytes
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class PauseSetInsteonAckMessageTwoBytes(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "02710304"
        self.cmd1 = int(0x03)
        self.cmd2 = int(0x04)

        kwargs = {"cmd1": self.cmd1, "cmd2": self.cmd2}

        super(PauseSetInsteonAckMessageTwoBytes, self).base_setup(
            MessageId.SET_ACK_MESSAGE_TWO_BYTES, unhexlify(self.hex), **kwargs
        )

        self.msg = set_ack_message_two_bytes(self.cmd1, self.cmd2)
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2


if __name__ == "__main__":
    unittest.main()
