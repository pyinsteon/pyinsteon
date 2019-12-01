from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId
from tests.utils import hex_to_inbound_message


class TestUserResetDetected(unittest.TestCase):

    def setUp(self):
        self.hex = '0255'
        self.message_id = MessageId(0x55)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        set_log_levels(logger='debug', logger_pyinsteon='info', logger_messages='info', logger_topics=False)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)