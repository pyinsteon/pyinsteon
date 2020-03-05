"""Test Set Insteon NAK Message Byte."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import set_nak_message_byte
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestSetInsteonNakMessageByte(unittest.TestCase, OutboundBase):
    """Test Set Insteon NAK Message Byte."""

    def setUp(self):
        """Set up test."""
        self.hex = "027003"
        self.cmd2 = int(0x03)

        kwargs = {"cmd2": self.cmd2}

        super(TestSetInsteonNakMessageByte, self).base_setup(
            MessageId.SET_NAK_MESSAGE_BYTE, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_cmd2(self):
        """Test cmd2."""
        assert self.msg.cmd2 == self.cmd2


if __name__ == "__main__":
    unittest.main()
