from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AllLinkMode
from pyinsteon.protocol.messages.outbound import start_all_linking

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStartAllLinking(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '02640304'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x64)
        self.mode = AllLinkMode(0x03)
        self.group = int(0x04)

        self.msg = start_all_linking(self.mode, self.group)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_mode(self):
        assert self.msg.mode == self.mode

    def test_group(self):
        assert self.msg.group == self.group


if __name__ == '__main__':
    unittest.main()
