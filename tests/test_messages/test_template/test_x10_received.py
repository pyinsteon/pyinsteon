from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.messages.template import x10_received

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestX10Received(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.message_id = MessageId(0x52)
        self.hex = '02520304'
        self.raw_x10 = int(0x03)
        self.x10_flag = int(0x04)

        self.msg_in, _ = hex_to_inbound_message(self.hex)
        self.msg = x10_received(self.raw_x10, self.x10_flag)

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_raw_x10(self):
        _LOGGER.debug(self.msg)
        assert self.msg.raw_x10 == self.raw_x10

    def test_x10_flag(self):
        _LOGGER.debug(self.msg)
        assert self.msg.x10_flag == self.x10_flag


if __name__ == '__main__':
    unittest.main()
