"""Test Set Insteon NAK Message Byte."""
import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import set_ack_message_two_bytes  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase
from tests.utils import async_case


class TestSetInsteonAckMessageTwoBytes(unittest.TestCase, OutboundBase):
    """Test Set Insteon ACK Message Two Bytes."""

    def setUp(self):
        """Set up test."""
        self.hex = "02710304"
        self.cmd1 = 0x03
        self.cmd2 = 0x04

        kwargs = {"cmd1": self.cmd1, "cmd2": self.cmd2}

        super(TestSetInsteonAckMessageTwoBytes, self).base_setup(
            MessageId.SET_ACK_MESSAGE_TWO_BYTES, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=True,
        )

    @async_case
    async def test_cmd1_cmd2(self):
        """Test cmd2."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.cmd1 == self.cmd1
        assert self.msg.cmd2 == self.cmd2


if __name__ == "__main__":
    unittest.main()
