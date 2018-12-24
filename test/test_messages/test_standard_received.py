from binascii import unhexlify
import logging
import unittest

from pyinsteon.address import Address
from pyinsteon.messages.message_flags import MessageFlags
from pyinsteon.messages import create_from_raw_data
from pyinsteon.messages.inbound_message import InboundMessage


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStandardReceived(unittest.TestCase):

    def setUp(self):
        self.hex_data = '0250010203040506070809'
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.address = Address('010203')
        self.target = Address('040506')
        self.flags = MessageFlags(0x07)
        self.cmd1 = int(0x08)
        self.cmd2 = int(0x09)

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

    def test_bytes(self):
        assert self.msg.bytes == self.bytes_data

    def test_hex(self):
        assert self.msg.hex == self.hex_data

    def test_len(self):
        assert len(self.msg) == 11


if __name__ == '__main__':
    _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()