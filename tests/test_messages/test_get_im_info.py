import unittest
from pyinsteon.constants import MessageId
from pyinsteon.messages.outbound import get_im_info

class GetImInfo(unittest.TestCase):

    def setUp(self):
        self.message_id = MessageId.GET_IM_INFO
        self.msg = get_im_info()

    def test_id(self):
        assert self.msg.message_id == self.message_id