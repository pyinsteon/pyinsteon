import sys
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import led_on
from tests import _LOGGER, set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestLedOn(unittest.TestCase, OutboundBase):
    def setUp(self):
        self.hex = "026D"
        super(TestLedOn, self).base_setup(MessageId.LED_ON, unhexlify(self.hex))
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
