from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AllLinkMode
from pyinsteon.protocol.messages.outbound import start_all_linking
from tests.test_messages.test_outbound.outbound_base import OutboundBase


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestStartAllLinking(unittest.TestCase, OutboundBase):

    def setUp(self):
        self.hex = '02640304'
        self.message_id = MessageId.START_ALL_LINKING
        self.mode = AllLinkMode(0x03)
        self.group = int(0x04)

        kwargs = {"group": self.group,
                  "mode": self.mode}

        super(TestStartAllLinking, self).base_setup(self.message_id,
                                                    unhexlify(self.hex),
                                                    **kwargs)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_mode(self):
        assert self.msg.mode == self.mode

    def test_group(self):
        assert self.msg.group == self.group


if __name__ == '__main__':
    unittest.main()
