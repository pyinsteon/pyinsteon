import logging
import unittest
import sys

from pyinsteon.constants import MessageId
from pyinsteon.address import Address
from pyinsteon.messages.template import all_link_cleanup_failure_report

from .template_base import TestTemplateBase
from ...utils import hex_to_inbound_message

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestAllLinkCleanupFailureReport(unittest.TestCase, TestTemplateBase):

    def setUp(self):
        self.hex = '02560304050607'
        self.message_id = MessageId(0x56)
        self.error = int(0x03)
        self.group = int(0x04)
        self.address = Address('050607')

        self.msg_in, _ = hex_to_inbound_message(self.hex)

        self.msg = all_link_cleanup_failure_report(
            self.error, self.group, self.address)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_error(self):
        assert self.msg.error == self.error

    def test_group(self):
        assert self.msg.group == self.group

    def test_address(self):
        assert self.msg.address == self.address


if __name__ == '__main__':
    unittest.main()
