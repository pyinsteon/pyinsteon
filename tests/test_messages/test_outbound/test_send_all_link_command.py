import logging
import sys
import unittest
from binascii import unhexlify

from pyinsteon.constants import AllLinkMode, MessageId
from pyinsteon.protocol.messages.outbound import send_all_link_command
from tests.test_messages.test_outbound.outbound_base import OutboundBase

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestSendAllLinkCommand(unittest.TestCase, OutboundBase):

    def setUp(self):
        self.hex = '02610101'
        self.group = 0x01
        self.mode = AllLinkMode.CONTROLLER
        
        kwargs = {"group": self.group,
                  "mode": self.mode}

        super(TestSendAllLinkCommand, self).base_setup(
            MessageId.SEND_ALL_LINK_COMMAND, unhexlify(self.hex), **kwargs)

        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_group(self):
        assert self.msg.group == self.group

    def test_mode(self):
        assert self.msg.mode == self.mode


if __name__ == '__main__':
    unittest.main()
