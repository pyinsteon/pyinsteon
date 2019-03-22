import logging
import sys
import unittest
from binascii import unhexlify

from pyinsteon.constants import AllLinkMode, MessageId
from pyinsteon.protocol.messages.outbound import send_all_link_command

try:
    from .outbound_base import TestOutboundBase
except ImportError:
    import outbound_base
    TestOutboundBase = outbound_base.TestOutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSendAllLinkCommand(unittest.TestCase, TestOutboundBase):

    def setUp(self):
        self.hex = '02610101'
        self.bytes_data = unhexlify(self.hex)
        self.message_id = MessageId.SEND_ALL_LINK_COMMAND
        self.group = 0x01
        self.cmd1 = 0x02

        self.msg = send_all_link_command(0x01, AllLinkMode.CONTROLLER)

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_group(self):
        assert self.msg.group == self.group

    def test_mode(self):
        assert self.msg.mode == AllLinkMode.CONTROLLER


if __name__ == '__main__':
    unittest.main()
