
from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import x10_send

from tests.test_messages.test_outbound.outbound_base import OutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestX10Send(unittest.TestCase, OutboundBase):

    def setUp(self):
        self.hex = '02630102'
        self.raw_x10 = int(0x01)
        self.x10_flag = int(0x02)

        kwargs = {'raw_x10': self.raw_x10,
                  'x10_flag': self.x10_flag}

        super(TestX10Send, self).base_setup(MessageId.X10_SEND,
                                            unhexlify(self.hex),
                                            **kwargs)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_raw_x10(self):
        assert self.msg.raw_x10 == self.raw_x10

    def test_x10_flag(self):
        assert self.msg.x10_flag == self.x10_flag


if __name__ == '__main__':
    unittest.main()
