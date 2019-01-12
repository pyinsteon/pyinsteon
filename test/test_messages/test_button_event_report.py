from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, ImButtonEvents
from ..utils import hex_to_inbpund_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestButtonEventReport(unittest.TestCase):

    def setUp(self):
        self.hex = '025403'
        self.id = MessageId(0x54)
        self.event = ImButtonEvents(0x03)

        self.msg, self.msg_bytes = hex_to_inbpund_message(self.hex)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.id == self.id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)