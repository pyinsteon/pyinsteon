import unittest
from pyinsteon.constants import MessageId, AllLinkMode
from pyinsteon.messages.outbound import send_all_link_command

class TestSendAllLinkCommand(unittest.TestCase):

    def setUp(self):
        self.message_id = MessageId.SEND_ALL_LINK_COMMAND
        self.group = 0x01
        self.cmd1 = 0x02

        self.msg = send_all_link_command(0x01, AllLinkMode.CONTROLLER)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_group(self):
        assert self.msg.group == self.group

    def test_mode(self):
        assert self.msg.mode == AllLinkMode.CONTROLLER
