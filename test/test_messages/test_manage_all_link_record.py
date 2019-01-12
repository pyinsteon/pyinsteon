from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak, ManageAlLinkRecordAction
from pyinsteon.address import Address
from pyinsteon.messages.all_link_record_flags import AllLinkRecordFlags
from ..utils import hex_to_inbpund_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestManageAllLinkRecord(unittest.TestCase):

    def setUp(self):
        self.hex = '026F400405060708090a0b'
        self.hex_ack = '026F400405060708090a0b06'
        self.id = MessageId(0x6F)
        self.action = ManageAlLinkRecordAction(0x40)
        self.flags = AllLinkRecordFlags(0x04)
        self.group = int(0x05)
        self.address = Address('060708')
        self.data1 = int(0x09)
        self.data2 = int(0x0a)
        self.data3 = int(0x0b)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbpund_message(self.hex_ack)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.id == self.id

    def test_ack_nak(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex_ack)