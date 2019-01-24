from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.address import Address
from ..utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestAllLinkCleanupFailureReport(unittest.TestCase):

    def setUp(self):
        self.hex = '02560304050607'
        self.message_id = MessageId(0x56)
        self.error = int(0x03)
        self.group = int(0x04)
        self.address = Address('050607')

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)


if __name__ == '__main__':
    unittest.main()