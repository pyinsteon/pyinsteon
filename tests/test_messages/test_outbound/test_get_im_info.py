import logging
import sys
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_im_info
from tests.test_messages.test_outbound.outbound_base import TestOutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')

class TestGetImInfo(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0260'
        super(TestGetImInfo, self).base_setup(MessageId.GET_IM_INFO, unhexlify(self.hex))

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
