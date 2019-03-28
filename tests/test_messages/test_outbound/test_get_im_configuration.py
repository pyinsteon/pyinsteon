from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_im_configuration
from tests.test_messages.test_outbound.outbound_base import TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetImConfiguration(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0273'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x73)
        super(TestGetImConfiguration, self).base_setup(MessageId(0x73), unhexlify(self.hex))

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
