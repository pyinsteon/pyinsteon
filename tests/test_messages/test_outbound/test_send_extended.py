from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.protocol.messages.outbound import send_extended
from pyinsteon.address import Address
from pyinsteon.protocol.messages.message_flags import MessageFlags
from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.user_data import UserData

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase



_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSendStandardAck(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex_data = '0262010203140506a1a2a3a4a5a6a7a8a9aaabacadae'
        self.bytes_data = unhexlify(self.hex_data)
        self.message_id = MessageId.SEND_STANDARD
        self.address = Address('010203')
        self.flags = MessageFlags(0x14)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.user_data = UserData(self.bytes_data[8:])

        self.msg = send_extended(address='010203', flags=0x14, cmd1=0x05, cmd2=0x06,
                                 user_data=self.bytes_data[8:])

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        # _LOGGER.setLevel(logging.DEBUG)

    def test_address(self):
        assert self.msg.address == self.address

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2

    def test_user_data(self):
        assert self.msg.user_data == self.user_data


if __name__ == '__main__':
    unittest.main()
