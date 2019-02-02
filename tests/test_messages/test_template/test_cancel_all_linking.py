"""Test cases for Cancel All Linking"""
import unittest
from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.template import cancel_all_linking

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message


class TestCancelAllLinking(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        super().setUp()
        self.hex = '0265'
        self.hex_ack = '026506'
        self.message_id = MessageId(0x65)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex_ack)
        self.msg = cancel_all_linking(self.ack)

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
