from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.address import Address
from pyinsteon.messages.message_flags import MessageFlags
from pyinsteon.messages import create_from_raw_data
from pyinsteon.messages.inbound_message import InboundMessage
from pyinsteon.constants import MessageId, MESSAGE_ACK, MESSAGE_NAK


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStandardSendAck(unittest.TestCase):

    def setUp(self):
        self.buffer = False
        self.hex_data = '026201020304050615'
        self.bytes_data = bytearray(unhexlify(self.hex_data))
        self.id = MessageId.SEND_STANDARD.value
        self.address = Address('010203')
        self.flags = MessageFlags(0x04)
        self.cmd1 = int(0x05)
        self.cmd2 = int(0x06)
        self.ack = MESSAGE_NAK

        self.msg = create_from_raw_data(self.bytes_data)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        _LOGGER.setLevel(logging.DEBUG)

    def test_id(self):
        assert self.msg.id == self.id

    def test_address(self):
        assert self.msg.address == self.address

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_cmd1(self):
        assert self.msg.cmd1 == self.cmd1

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2

    def test_ack(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert self.msg.bytes == self.bytes_data

    def test_hex(self):
        assert self.msg.hex == self.hex_data

    def test_len(self):
        assert len(self.msg) == 9


if __name__ == '__main__':
    _INSTEON_LOGGER.setLevel(logging.DEBUG)
    unittest.main(buffer=False)