"""Test cases for Cancel All Linking"""
from binascii import unhexlify
import unittest
from pyinsteon.constants import MessageId
from tests.test_messages.test_outbound.outbound_base import TestOutboundBase


class TestCancelAllLinking(unittest.TestCase, TestOutboundBase):
    """Test Cancel All-Linking command."""
    def setUp(self):
        #pylint: disable=unused-import
        from pyinsteon.protocol.messages.outbound import cancel_all_linking
        self.hex = '0265'
        super(TestCancelAllLinking, self).base_setup(MessageId(0x65), unhexlify(self.hex))

if __name__ == '__main__':
    unittest.main()
