from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.im_config_flags import IMConfigurationFlags
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetImConfiguration(unittest.TestCase):

    def setUp(self):
        self.hex = '0273'
        self.hex_ack = '027330040506'
        self.message_id = MessageId(0x73)
        self.flags = IMConfigurationFlags(0x30)
        self.spare1 = int(0x04)
        self.spare2 = int(0x05)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex_ack)
        
        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex_ack)