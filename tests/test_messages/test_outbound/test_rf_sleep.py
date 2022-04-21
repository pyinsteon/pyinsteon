"""Test RF Sleep."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import rf_sleep  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestRfSleep(unittest.TestCase, OutboundBase):
    """Test RF Sleep."""

    def setUp(self):
        """Test set up."""
        self.hex = "0272"
        super(TestRfSleep, self).base_setup(MessageId.RF_SLEEP, unhexlify(self.hex))
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
