"""Test All-Link Cleanup Failure Report."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MessageId

# pylint: disable=unused-import
# flake8: noqa: F401
from pyinsteon.handlers.all_link_cleanup_failure_report import (
    AllLinkCleanupFailureReport,
)
from tests import set_log_levels
from tests.utils import hex_to_inbound_message


class TestAllLinkCleanupFailureReport(unittest.TestCase):
    """Test All-Link Cleanup Failure Report."""

    def setUp(self):
        """Set up test."""
        self.hex = "02560304050607"
        self.message_id = MessageId(0x56)
        self.error = int(0x03)
        self.group = int(0x04)
        self.address = Address("050607")

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_id(self):
        """Test Id."""
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        """Test bytes."""
        assert bytes(self.msg) == unhexlify(self.hex)


if __name__ == "__main__":
    unittest.main()
