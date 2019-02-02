from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.messages.template import user_reset_detected

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestUserResetDetected(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '0255'
        self.message_id = MessageId(0x55)

        self.msg_in, _ = hex_to_inbound_message(self.hex)
        self.msg = user_reset_detected()
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)


if __name__ == '__main__':
    unittest.main()
