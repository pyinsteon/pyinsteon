"""Test cases for Cancel All Linking"""
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
# pylint: disable=unused-import
from pyinsteon.protocol.messages.outbound import cancel_all_linking
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestCancelAllLinking(unittest.TestCase, OutboundBase):
    """Test Cancel All-Linking command."""

    def setUp(self):

        self.hex = "0265"
        super(TestCancelAllLinking, self).base_setup(
            MessageId(0x65), unhexlify(self.hex)
        )


if __name__ == "__main__":
    unittest.main()
