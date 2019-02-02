from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.template import get_all_link_record_for_sender

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetAllLinkRecordForSender(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '026C'
        self.hex_ack = '026C06'
        self.message_id = MessageId(0x6C)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = get_all_link_record_for_sender(self.ack)
        
        stream_handler = logging.StreamHandler(sys.stdout)

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
