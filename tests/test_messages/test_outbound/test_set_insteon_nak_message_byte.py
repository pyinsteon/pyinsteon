from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import set_nak_message_byte
from tests.test_messages.test_outbound.outbound_base import OutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetInsteonNakMessageByte(unittest.TestCase, OutboundBase):

    def setUp(self):
        self.hex = '027003'
        self.cmd2 = int(0x03)

        kwargs = {'cmd2': self.cmd2}

        super(TestSetInsteonNakMessageByte, self).base_setup(MessageId.SET_NAK_MESSAGE_BYTE,
                                                             unhexlify(self.hex),
                                                             **kwargs)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_cmd2(self):
        assert self.msg.cmd2 == self.cmd2


if __name__ == '__main__':
    unittest.main()
