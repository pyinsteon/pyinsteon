from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak, DeviceCategory
from pyinsteon.address import Address
from pyinsteon.messages.template import get_im_info

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetImInfo(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '0260'
        self.hex_ack = '026003040507070806'
        self.message_id = MessageId(0x60)
        self.address = Address('030405')
        self.cat = DeviceCategory(0x07)
        self.subcat = int(0x07)
        self.firmware = int(0x08)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = get_im_info(self.address, self.cat, self.subcat,
                               self.firmware, self.ack)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_address(self):
        assert self.msg.address == self.address

    def test_cat(self):
        assert self.msg.cat == self.cat

    def test_subcat(self):
        assert self.msg.subcat == self.subcat

    def test_firmware(self):
        assert self.msg.firmware == self.firmware

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
