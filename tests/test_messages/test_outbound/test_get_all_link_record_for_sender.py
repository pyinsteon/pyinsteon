from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_all_link_record_for_sender

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetAllLinkRecordForSender(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026C'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x6C)

        self.msg = get_all_link_record_for_sender()
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
