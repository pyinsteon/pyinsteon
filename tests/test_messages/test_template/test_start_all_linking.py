from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak, AllLinkMode
from pyinsteon.messages.template import start_all_linking

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStartAllLinking(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '02640304'
        self.hex_ack = '0264030406'
        self.message_id = MessageId(0x64)
        self.mode = AllLinkMode(0x03)
        self.group = int(0x04)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = start_all_linking(self.mode, self.group, self.ack)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_mode(self):
        assert self.msg.mode == self.mode

    def test_group(self):
        assert self.msg.group == self.group

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
