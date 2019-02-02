
from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.template import x10_send

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestX10Send(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '02630102'
        self.hex_ack = '0263010206'
        self.message_id = MessageId(0x63)
        self.raw_x10 = int(0x01)
        self.x10_flag = int(0x02)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = x10_send(self.raw_x10, self.x10_flag, self.ack)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_raw_x10(self):
        assert self.msg.raw_x10 == self.raw_x10

    def test_x10_flag(self):
        assert self.msg.x10_flag == self.x10_flag

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
