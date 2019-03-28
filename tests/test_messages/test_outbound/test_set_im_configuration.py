from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.protocol.messages.im_config_flags import IMConfigurationFlags
from pyinsteon.protocol.messages.outbound import set_im_configuration
from tests.test_messages.test_outbound.outbound_base import TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSetImConfiguration(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '026B30'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId.SET_IM_CONFIGURATION
        self.flags = IMConfigurationFlags(0x30)

        kwargs = {'flags': self.flags}

        super(TestSetImConfiguration, self).base_setup(self.message_id,
                                                       unhexlify(self.hex),
                                                       **kwargs)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_flags(self):
        assert self.msg.flags == self.flags


if __name__ == '__main__':
    unittest.main()
