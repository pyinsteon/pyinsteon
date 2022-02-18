"""Test Get Next All-Link Record."""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import get_next_all_link_record  # noqa: F401
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetNextAllLinkRecord(unittest.TestCase, OutboundBase):
    """Test Get Next All-Link Record."""

    def setUp(self):
        """Test set up."""
        self.hex = "026A"
        super(TestGetNextAllLinkRecord, self).base_setup(
            MessageId.GET_NEXT_ALL_LINK_RECORD, unhexlify(self.hex)
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
