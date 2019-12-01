"""Test sending extended message."""

import unittest

from binascii import unhexlify
from tests import set_log_levels
from tests.test_messages.test_outbound.outbound_base import OutboundBase

from pyinsteon.address import Address
from pyinsteon.protocol.messages.message_flags import MessageFlags
from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.user_data import UserData
#pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import send_extended



class TestSendExtended(unittest.TestCase, OutboundBase):

    def setUp(self):
        self.hex = '0262010203140506a1a2a3a4a5a6a7a8a9aaabacadae'
        self.message_id = MessageId.SEND_EXTENDED
        self.address = Address('010203')
        self.flags = MessageFlags(0x14)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.user_data = UserData(unhexlify(self.hex)[8:])

        kwargs = {'address': self.address,
                  'flags': self.flags,
                  'cmd1': self.cmd1,
                  'cmd2': self.cmd2,
                  'user_data': self.user_data}

        super(TestSendExtended, self).base_setup(MessageId.SEND_EXTENDED,
                                                 unhexlify(self.hex), **kwargs)
        set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='info', logger_topics=True)

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
