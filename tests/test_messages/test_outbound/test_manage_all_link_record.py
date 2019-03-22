from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, ManageAllLinkRecordAction
from pyinsteon.address import Address
from pyinsteon.protocol.messages.all_link_record_flags import AllLinkRecordFlags
from pyinsteon.protocol.messages.outbound import manage_all_link_record

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase



_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestManageAllLinkRecord(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026F400405060708090a0b'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x6F)
        self.action = ManageAllLinkRecordAction(0x40)
        self.flags = AllLinkRecordFlags(0x04)
        self.group = int(0x05)
        self.address = Address('060708')
        self.data1 = int(0x09)
        self.data2 = int(0x0a)
        self.data3 = int(0x0b)

        self.msg = manage_all_link_record(self.action, self.flags, self.group,
                                          self.address, self.data1, self.data2,
                                          self.data3)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_action(self):
        assert self.msg.action == self.action

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_group(self):
        assert self.msg.group == self.group

    def test_address(self):
        assert self.msg.address == self.address

    def test_data1(self):
        assert self.msg.data1 == self.data1

    def test_data2(self):
        assert self.msg.data2 == self.data2

    def test_data3(self):
        assert self.msg.data3 == self.data3


if __name__ == '__main__':
    unittest.main()
