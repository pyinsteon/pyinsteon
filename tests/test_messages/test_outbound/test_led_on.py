"""Test LED On."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import led_on  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestLedOn(unittest.TestCase, OutboundBase):
    """Test LED On."""

    def setUp(self):
        """Test set up."""
        self.hex = "026D"
        super(TestLedOn, self).base_setup(MessageId.LED_ON, unhexlify(self.hex))
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
