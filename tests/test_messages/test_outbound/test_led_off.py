from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.outbound import led_off

from .outbound_base import TestOutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestLedOff(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026E'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x6E)

        self.msg = led_off()
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
