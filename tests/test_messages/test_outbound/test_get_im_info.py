from binascii import unhexlify
import unittest
from pyinsteon.constants import MessageId
from pyinsteon.messages.outbound import get_im_info

from .outbound_base import TestOutboundBase

class GetImInfo(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0260'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId.GET_IM_INFO
        self.msg = get_im_info()
