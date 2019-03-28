
from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_first_all_link_record
from tests.test_messages.test_outbound.outbound_base import TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetFirstAllLinkRecord(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0269'
        super(TestGetFirstAllLinkRecord, self).base_setup(MessageId(0x69), unhexlify(self.hex))

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
