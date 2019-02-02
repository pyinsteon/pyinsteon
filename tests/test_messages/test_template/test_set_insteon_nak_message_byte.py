from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.template import set_nak_message_byte

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetInsteonNakMessageByte(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '027003'
        self.hex_ack = '02700306'
        self.message_id = MessageId(0x70)
        self.cmd2 = int(0x03)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = set_nak_message_byte(self.cmd2, self.ack)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
