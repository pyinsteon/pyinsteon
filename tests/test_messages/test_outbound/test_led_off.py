"""Test LED Off."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import led_off  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestLedOff(unittest.TestCase, OutboundBase):
    """Test LED Off."""

    def setUp(self):
        """Test set up."""
        self.hex = "026E"
        super(TestLedOff, self).base_setup(MessageId.LED_OFF, unhexlify(self.hex))
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
