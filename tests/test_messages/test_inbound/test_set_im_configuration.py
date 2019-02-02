from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.im_config_flags import IMConfigurationFlags
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetImConfiguration(unittest.TestCase):

    def setUp(self):
        self.hex = '026B30'
        self.hex_ack = '026B3006'
        self.message_id = MessageId(0x6B)
        self.flags = IMConfigurationFlags(0x30)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_ack)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        _LOGGER.debug(bytes(self.msg))
        _LOGGER.debug(unhexlify(self.hex_ack))
        assert bytes(self.msg) == unhexlify(self.hex_ack)


if __name__ == '__main__':
    unittest.main()