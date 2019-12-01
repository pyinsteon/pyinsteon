"""Test Get All-Link Record for Sender Command."""
from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId
#pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import get_all_link_record_for_sender
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetAllLinkRecordForSender(unittest.TestCase, OutboundBase):
    """Test Get All-Link Record for Sender Command."""

    def setUp(self):
        self.hex = '026C'
        super(TestGetAllLinkRecordForSender, self).base_setup(MessageId(0x6C), unhexlify(self.hex))
        set_log_levels(logger='debug', logger_pyinsteon='info', logger_messages='info', logger_topics=False)


if __name__ == '__main__':
    unittest.main()
