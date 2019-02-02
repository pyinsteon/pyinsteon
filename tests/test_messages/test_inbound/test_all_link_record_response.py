from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.address import Address
from pyinsteon.messages.all_link_record_flags import AllLinkRecordFlags
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestAllLinkRecordResponse(unittest.TestCase):

    def setUp(self):
        self.hex = '0257030405060708090a'
        self.message_id = MessageId(0x57)
        self.flags = AllLinkRecordFlags(0x03)
        self.group = int(0x04)
        self.address = Address('050607')
        self.data1 = int(0x08)
        self.data2 = int(0x09)
        self.data3 = int(0x0a)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)