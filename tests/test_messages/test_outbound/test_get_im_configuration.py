from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.messages.outbound import get_im_configuration

from .outbound_base import TestOutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestGetImConfiguration(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '0273'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId(0x73)

        self.msg = get_im_configuration()

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
