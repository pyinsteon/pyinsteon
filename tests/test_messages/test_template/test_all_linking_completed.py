from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.address import Address
from pyinsteon.constants import MessageId, AllLinkMode, DeviceCategory
from pyinsteon.messages.template import all_linking_completed

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestAllLinkingCompleted(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.message_id = MessageId(0x53)
        self.hex = '0253030405060708090a'
        self.mode = AllLinkMode(0x03)
        self.group = int(0x04)
        self.address = Address('050607')
        self.cat = DeviceCategory(0x08)
        self.subcat = int(0x09)
        self.firmware = int(0x0a)

        self.msg_in, _ = hex_to_inbound_message(self.hex)
        self.msg = all_linking_completed(self.mode, self.group, self.address,
                                         self.cat, self.subcat, self.firmware)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_mode(self):
        assert self.msg.mode == self.mode

    def test_group(self):
        assert self.msg.group == self.group

    def test_address(self):
        assert self.msg.address == self.address

    def test_cat(self):
        assert self.msg.cat == self.cat

    def test_subcat(self):
        assert self.msg.subcat == self.subcat

    def test_firmware(self):
        assert self.msg.firmware == self.firmware


if __name__ == '__main__':
    unittest.main()