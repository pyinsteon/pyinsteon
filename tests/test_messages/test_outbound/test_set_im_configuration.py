from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.im_config_flags import IMConfigurationFlags
from pyinsteon.protocol.messages.outbound import set_im_configuration

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetImConfiguration(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026B30'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x6B)
        self.flags = IMConfigurationFlags(0x30)

        self.msg = set_im_configuration(self.flags)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_flags(self):
        assert self.msg.flags == self.flags


if __name__ == '__main__':
    unittest.main()
