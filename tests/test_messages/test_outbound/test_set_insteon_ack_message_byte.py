from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.messages.outbound import set_ack_message_byte

from .outbound_base import TestOutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetInsteonAckMessageByte(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026803'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x68)
        self.cmd2 = int(0x03)

        self.msg = set_ack_message_byte(self.cmd2)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2


if __name__ == '__main__':
    unittest.main()
