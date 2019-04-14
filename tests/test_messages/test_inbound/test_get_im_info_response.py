from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak, DeviceCategory
from pyinsteon.address import Address
from tests.utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetImInfoResponse(unittest.TestCase):

    def setUp(self):
        self.hex = '0260'
        self.hex_ack = '026003040507070806'
        self.message_id = MessageId(0x60)
        self.address = Address('030405')
        self.cat = DeviceCategory(0x07)
        self.subcat = int(0x07)
        self.firmware = int(0x08)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_ack)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex_ack)