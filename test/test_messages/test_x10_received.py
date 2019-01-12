from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from ..utils import hex_to_inbpund_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestX10Received(unittest.TestCase):

    def setUp(self):
        self.id = MessageId(0x52)
        self.hex = '02520304'
        self.raw_x10 = int(0x03)
        self.x10_flag = int(0x04)

        self.msg, self.msg_bytes = hex_to_inbpund_message(self.hex)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.id == self.id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)