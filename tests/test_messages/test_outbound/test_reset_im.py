from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import reset_im
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestResetIm(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "0267"
        super(TestResetIm, self).base_setup(MessageId.RESET_IM, unhexlify(self.hex))
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
