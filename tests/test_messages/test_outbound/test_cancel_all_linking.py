"""Test cases for Cancel All Linking"""
from binascii import unhexlify
import unittest
from pyinsteon.constants import MessageId
from pyinsteon.messages.outbound import cancel_all_linking

from .outbound_base import TestOutboundBase


class TestCancelAllLinking(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0265'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x65)

        self.msg = cancel_all_linking()


if __name__ == '__main__':
    unittest.main()
