from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.constants import MessageId, ImButtonEvents
from pyinsteon.messages.template import button_event_report

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestButtonEventReport(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '025403'
        self.message_id = MessageId(0x54)
        self.event = ImButtonEvents(0x03)

        self.msg_in, _ = hex_to_inbound_message(self.hex)
        self.msg = button_event_report(self.event)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_event(self):
        assert self.msg.event == self.event


if __name__ == '__main__':
    unittest.main()