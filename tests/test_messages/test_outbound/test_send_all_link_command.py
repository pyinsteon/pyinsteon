from binascii import unhexlify
import unittest
from pyinsteon.constants import MessageId, AllLinkMode
from pyinsteon.messages.outbound import send_all_link_command

from .outbound_base import TestOutboundBase


class TestSendAllLinkCommand(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '02610101'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId.SEND_ALL_LINK_COMMAND
        self.group = 0x01
        self.cmd1 = 0x02

        self.msg = send_all_link_command(0x01, AllLinkMode.CONTROLLER)

    def test_group(self):
        assert self.msg.group == self.group

    def test_mode(self):
        assert self.msg.mode == AllLinkMode.CONTROLLER
