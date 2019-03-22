from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_next_all_link_record

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetNextAllLinkRecord(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026A'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x6A)

        self.msg = get_next_all_link_record()
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
