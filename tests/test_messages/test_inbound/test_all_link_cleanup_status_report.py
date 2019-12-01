from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from tests.utils import hex_to_inbound_message


class TestAllLinkCleanupStatusReport(unittest.TestCase):

    def setUp(self):
        self.hex = '025806'
        self.message_id = MessageId(0x58)
        self.ack = AckNak(0x06)

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        set_log_levels(logger='debug', logger_pyinsteon='info', logger_messages='info', logger_topics=False)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_ack_nak(self):
        assert self.msg.ack == self.ack

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)


if __name__ == '__main__':
    unittest.main()