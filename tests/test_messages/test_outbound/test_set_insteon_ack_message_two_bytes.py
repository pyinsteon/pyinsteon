
from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.outbound import set_ack_message_two_bytes

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase



_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetInsteonAckMessageTwoBytes(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '02710304'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x71)
        self.cmd1 = int(0x03)
        self.cmd2 = int(0x04)

        self.msg = set_ack_message_two_bytes(self.cmd1, self.cmd2)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2


if __name__ == '__main__':
    unittest.main()
