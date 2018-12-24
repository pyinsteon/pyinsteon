from binascii import unhexlify
import logging
import unittest

from pyinsteon.address import Address
from pyinsteon.messages.message_flags import MessageFlags
from pyinsteon.messages import create_from_raw_data
from pyinsteon.messages.inbound_message import InboundMessage


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStandardInMessageCreate(unittest.TestCase):

    def setUp(self):
        self.data = bytearray(unhexlify('0250112233445566778899'))
        self.address = Address('112233')
        self.target = Address('445566')
        self.flags = MessageFlags(0x77)
        self.cmd1 = int(0x88)
        self.cmd2 = int(0x99)

        self.msg = create_from_raw_data(self.data)

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


if __name__ == '__main__':
    _LOGGER.setLevel(logging.DEBUG)
    _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()