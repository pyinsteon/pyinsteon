from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.outbound import rf_sleep

from .outbound_base import TestOutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestRfSleep(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0272'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x72)

        self.msg = rf_sleep()

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
