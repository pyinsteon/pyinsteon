from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.outbound import led_off
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestLedOff(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "026E"
        super(TestLedOff, self).base_setup(MessageId.LED_OFF, unhexlify(self.hex))
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
