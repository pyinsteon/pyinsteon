from binascii import unhexlify
from tests import _LOGGER, set_log_levels
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_im_configuration
from tests.test_messages.test_outbound.outbound_base import OutboundBase


class TestGetImConfiguration(unittest.TestCase, OutboundBase):

    def setUp(self):
        self.hex = '0273'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x73)
        super(TestGetImConfiguration, self).base_setup(MessageId(0x73), unhexlify(self.hex))
        set_log_levels(logger='debug', logger_pyinsteon='info', logger_messages='info', logger_topics=False)

if __name__ == '__main__':
    unittest.main()
