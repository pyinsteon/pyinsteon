from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak, DeviceCategory
from pyinsteon.messages.template import set_host_dev_cat

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetHostDeviceCategory(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '0266030405'
        self.hex_ack = '026603040506'
        self.message_id = MessageId(0x66)
        self.cat = DeviceCategory(0x03)
        self.subcat = int(0x04)
        self.firmware = int(0x05)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = set_host_dev_cat(self.cat, self.subcat, self.firmware,
                                    self.ack)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

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
