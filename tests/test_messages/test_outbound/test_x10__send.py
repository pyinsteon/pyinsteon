from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import x10_send

from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestX10Send(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "02630102"
        self.raw_x10 = int(0x01)
        self.x10_flag = int(0x02)

        kwargs = {"raw_x10": self.raw_x10, "x10_flag": self.x10_flag}

        super(TestX10Send, self).base_setup(
            MessageId.X10_SEND, unhexlify(self.hex), **kwargs
        )
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_raw_x10(self):
        assert self.msg.raw_x10 == self.raw_x10

    def test_x10_flag(self):
        assert self.msg.x10_flag == self.x10_flag


if __name__ == "__main__":
    unittest.main()
