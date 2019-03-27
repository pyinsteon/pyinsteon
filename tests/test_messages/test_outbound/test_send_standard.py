from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.protocol.messages.outbound import send_standard
from pyinsteon.address import Address
from pyinsteon.protocol.messages.message_flags import MessageFlags
from pyinsteon.constants import MessageId, MESSAGE_NAK

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase



_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSendStandard(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0262010203040506'
        self.message_id = MessageId.SEND_STANDARD
        self.address = Address('010203')
        self.flags = MessageFlags(0x04)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)

        kwargs = {'address': self.address,
                  'flags': self.flags,
                  'cmd1': self.cmd1,
                  'cmd2': self.cmd2}

        super(TestSendStandard, self).base_setup(MessageId.SEND_STANDARD,
                                                 unhexlify(self.hex), **kwargs)

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


if __name__ == '__main__':
    unittest.main()
