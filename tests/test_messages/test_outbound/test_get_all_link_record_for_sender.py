"""Test Get All-Link Record for Sender Command."""

import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId

# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import (  # noqa: F401
    get_all_link_record_for_sender,
)
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetAllLinkRecordForSender(unittest.TestCase, OutboundBase):
    """Test Get All-Link Record for Sender Command."""

    def setUp(self):
        """Set up TestGetAllLinkRecordForSender tests."""
        self.hex = "026C"
        super(TestGetAllLinkRecordForSender, self).base_setup(
            MessageId(0x6C), unhexlify(self.hex)
        )
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )


if __name__ == "__main__":
    unittest.main()
