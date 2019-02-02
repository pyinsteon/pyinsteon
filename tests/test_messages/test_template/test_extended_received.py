from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.address import Address
from pyinsteon.messages.template import extended_received
from pyinsteon.messages.message_flags import MessageFlags
from pyinsteon.messages.user_data import UserData

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestExtendedSendAck(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex_data = '0251112233445566778899a1a2a3a4a5a6a7a8a9aaabacadae'
        self.message_id = 0x51
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.address = Address('112233')
        self.target = Address('445566')
        self.flags = MessageFlags(0x77)
        self.cmd1 = int(0x88)
        self.cmd2 = int(0x99)
        self.user_data = UserData(unhexlify('a1a2a3a4a5a6a7a8a9aaabacadae'))

        self.msg_in, _ = hex_to_inbound_message(self.hex_data)
        self.msg = extended_received(self.address, self.target, self.flags,
                                     self.cmd1, self.cmd2, self.user_data)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        _INSTEON_LOGGER.addHandler(stream_handler)

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

    def test_user_data(self):
        assert self.msg.user_data == self.user_data


if __name__ == '__main__':
    # _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main()