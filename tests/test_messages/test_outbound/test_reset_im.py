from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.outbound import reset_im

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestResetIm(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0267'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x67)
        self.ack = AckNak(0x06)

        self.msg = reset_im()
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
