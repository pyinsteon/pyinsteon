from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.outbound import led_on

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestLedOn(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026D'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x6D)
        self.ack = AckNak(0x06)

        self.msg = led_on()

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
