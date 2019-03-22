import logging
import sys
import unittest
from binascii import unhexlify

from pyinsteon.constants import MessageId
from pyinsteon.protocol.messages.outbound import get_im_info

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')

class GetImInfo(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0260'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId.GET_IM_INFO
        self.msg = get_im_info()

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
