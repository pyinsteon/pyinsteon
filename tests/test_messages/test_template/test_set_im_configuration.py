from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.im_config_flags import IMConfigurationFlags
from pyinsteon.messages.template import set_im_configuration

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetImConfiguration(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '026B30'
        self.hex_ack = '026B3006'
        self.message_id = MessageId(0x6B)
        self.flags = IMConfigurationFlags(0x30)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = set_im_configuration(self.flags, self.ack)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_flags(self):
        assert self.msg.flags == self.flags

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
