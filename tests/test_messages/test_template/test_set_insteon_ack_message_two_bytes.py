
from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.template import set_ack_message_two_bytes

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetInsteonAckMessageTwoBytes(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '02710304'
        self.hex_ack = '0271030406'
        self.message_id = MessageId(0x71)
        self.cmd1 = int(0x03)
        self.cmd2 = int(0x04)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = set_ack_message_two_bytes(self.cmd1, self.cmd2, self.ack)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
