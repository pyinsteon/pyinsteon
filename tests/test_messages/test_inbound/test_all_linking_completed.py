from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.address import Address
from pyinsteon.constants import MessageId, AllLinkMode, DeviceCategory
from tests.utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestAllLinkingCompleted(unittest.TestCase):

    def setUp(self):
        self.message_id = MessageId(0x53)
        self.hex = '0253030405060708090a'
        self.mode = AllLinkMode(0x03)
        self.group = int(0x04)
        self.address = Address('050607')
        self.cat = DeviceCategory(0x08)
        self.subcat = int(0x09)
        self.firmware = int(0x0a)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)