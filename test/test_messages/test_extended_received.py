from binascii import unhexlify
import logging
import unittest

from pyinsteon.address import Address
from pyinsteon.messages import create_from_raw_data
from pyinsteon.messages.inbound_message import InboundMessage
from pyinsteon.messages.message_flags import MessageFlags
from pyinsteon.messages.user_data import UserData


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestExtendedReceived(unittest.TestCase):

    def setUp(self):
        self.hex_data = '0250112233445566778899a1a2a3a4a5a6a7a8a9aaabacadae'
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.address = Address('112233')
        self.target = Address('445566')
        self.flags = MessageFlags(0x77)
        self.cmd1 = int(0x88)
        self.cmd2 = int(0x99)
        self.userdata = UserData(unhexlify('a1a2a3a4a5a6a7a8a9aaabacadae'))

        self.msg = create_from_raw_data(self.bytes_data)

    def test_address(self):
        assert self.msg.address == self.address

    def test_target(self):
        assert self.msg.target == self.target

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2

    def test_userdata(self):
        assert self.msg.userdata == self.userdata

    def test_bytes(self):
        assert self.msg.bytes == self.bytes_data

    def test_hex(self):
        assert self.msg.hex == self.hex_data

    def test_len(self):
        assert len(self.msg) == 25


if __name__ == '__main__':
    _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()