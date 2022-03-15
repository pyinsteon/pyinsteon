"""Text X10 Send message."""
import unittest
from binascii import unhexlify

from pyinsteon import pub
from pyinsteon.constants import MessageId
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase
from tests.utils import async_case


class TestX10Send(unittest.TestCase, OutboundBase):
    """Test the X10 Send command."""

    def setUp(self):
        """Set up the test."""
        self.hex = "0263ef00"
        self.raw_x10 = int(0xEF)
        self.x10_flag = int(0x00)

        kwargs = {"raw_x10": self.raw_x10, "x10_flag": self.x10_flag}

        super(TestX10Send, self).base_setup(
            MessageId.X10_SEND, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    @async_case
    async def test_raw_x10(self):
        """Test the raw x10 byte."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.raw_x10 == self.raw_x10

    @async_case
    async def test_x10_flag(self):
        """Test the x10 flag byte."""
        pub.sendMessage("send.{}".format(self.topic), **self.kwargs)
        assert self.msg.x10_flag == self.x10_flag


if __name__ == "__main__":
    unittest.main()
