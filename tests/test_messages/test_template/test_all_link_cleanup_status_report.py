import logging
import unittest
import sys

from pyinsteon.constants import MessageId, AckNak
from pyinsteon.messages.template import all_link_cleanup_status_report

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestAllLinkCleanupStatusReport(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '025806'
        self.message_id = MessageId(0x58)
        self.ack = AckNak(0x06)

        self.msg_in, _ = hex_to_inbound_message(self.hex)
        self.msg = all_link_cleanup_status_report(self.ack)

        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_ack_nak(self):
        assert self.msg.ack == self.ack


if __name__ == '__main__':
    unittest.main()
