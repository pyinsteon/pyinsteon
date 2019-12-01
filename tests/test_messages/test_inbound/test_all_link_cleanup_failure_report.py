import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from pyinsteon.constants import MessageId
from tests import _LOGGER, set_log_levels
from tests.utils import hex_to_inbound_message


class TestAllLinkCleanupFailureReport(unittest.TestCase):

    def setUp(self):
        self.hex = '02560304050607'
        self.message_id = MessageId(0x56)
        self.error = int(0x03)
        self.group = int(0x04)
        self.address = Address('050607')

        self.msg, self.msg_bytes = hex_to_inbound_message(self.hex)
        set_log_levels(logger='debug', logger_pyinsteon='info', logger_messages='info', logger_topics=False)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        assert bytes(self.msg) == unhexlify(self.hex)


if __name__ == '__main__':
    unittest.main()
