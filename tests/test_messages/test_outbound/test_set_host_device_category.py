from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, DeviceCategory
from pyinsteon.protocol.messages.outbound import set_host_dev_cat

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetHostDeviceCategory(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0266030405'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x66)
        self.cat = DeviceCategory(0x03)
        self.subcat = int(0x04)
        self.firmware = int(0x05)

        self.msg = set_host_dev_cat(self.cat, self.subcat, self.firmware)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_cat(self):
        assert self.msg.cat == self.cat

    def test_subcat(self):
        assert self.msg.subcat == self.subcat

    def test_firmware(self):
        assert self.msg.firmware == self.firmware


if __name__ == '__main__':
    unittest.main()
