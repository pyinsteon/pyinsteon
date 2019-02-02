
from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.outbound import x10_send

from .outbound_base import TestOutboundBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestX10Send(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '02630102'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x63)
        self.raw_x10 = int(0x01)
        self.x10_flag = int(0x02)

        self.msg = x10_send(self.raw_x10, self.x10_flag)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_raw_x10(self):
        assert self.msg.raw_x10 == self.raw_x10

    def test_x10_flag(self):
        assert self.msg.x10_flag == self.x10_flag


if __name__ == '__main__':
    unittest.main()
