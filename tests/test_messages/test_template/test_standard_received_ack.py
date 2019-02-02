from binascii import unhexlify
import logging
import unittest

from pyinsteon.address import Address
from pyinsteon.messages.message_flags import MessageFlags
from pyinsteon.messages.inbound import Inbound, create
from pyinsteon.messages.template import standard_received

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStandardReceived(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex_data = '0250010203040506070809'
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.message_id = 0x50
        self.address = Address('010203')
        self.target = Address('040506')
        self.flags = MessageFlags(0x07)
        self.cmd1 = int(0x08)
        self.cmd2 = int(0x09)

        self.msg_in, _ = hex_to_inbound_message(self.hex_data)
        self.msg = standard_received(self.address, self.target, self.flags,
                                     self.cmd1, self.cmd2)

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
    unittest.main()
