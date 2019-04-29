from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_next_all_link_record
from tests.test_messages.test_outbound.outbound_base import OutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetNextAllLinkRecord(unittest.TestCase, OutboundBase):

    def setUp(self):
        self.hex = '026A'
        super(TestGetNextAllLinkRecord, self).base_setup(MessageId.GET_NEXT_ALL_LINK_RECORD,
                                                         unhexlify(self.hex))

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
