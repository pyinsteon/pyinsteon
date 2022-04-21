"""Test Get First All Link Record."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import get_first_all_link_record  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetFirstAllLinkRecord(unittest.TestCase, OutboundBase):
    """Test Get First All Link Record."""

    def setUp(self):
        """Set up test."""
        self.hex = "0269"
        super(TestGetFirstAllLinkRecord, self).base_setup(
            MessageId(0x69), unhexlify(self.hex)
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
