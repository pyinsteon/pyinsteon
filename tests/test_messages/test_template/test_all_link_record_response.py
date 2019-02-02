from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.address import Address
from pyinsteon.messages.all_link_record_flags import AllLinkRecordFlags
from pyinsteon.messages.template import all_link_record_response

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestAllLinkRecordResponse(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '0257030405060708090a'
        self.message_id = MessageId(0x57)
        self.flags = AllLinkRecordFlags(0x03)
        self.group = int(0x04)
        self.address = Address('050607')
        self.data1 = int(0x08)
        self.data2 = int(0x09)
        self.data3 = int(0x0a)

        self.msg_in, _ = hex_to_inbound_message(self.hex)
        self.msg = all_link_record_response(
            self.flags, self.group, self.address,
            self.data1, self.data2, self.data3)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_group(self):
        assert self.msg.group == self.group

    def test_address(self):
        assert self.msg.address == self.address

    def test_data1(self):
        assert self.msg.data1 == self.data1

    def test_data2(self):
        assert self.msg.data2 == self.data2

    def test_data3(self):
        assert self.msg.data3 == self.data3


if __name__ == '__main__':
    unittest.main()
