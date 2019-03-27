"""Base class for testing outbound messages."""

import logging
import unittest
import sys

from pyinsteon import pub
from pyinsteon.constants import MessageId
from tests.utils import check_fields_match


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


stream_handler = logging.StreamHandler(sys.stdout)
_LOGGER.addHandler(stream_handler)
_INSTEON_LOGGER.addHandler(stream_handler)


class TestOutboundBase():

    def base_setup(self, message_id, bytes_data, **kwargs):
        """Init the TestOutboundBase class."""
        self.msg = None
        self.message_id = message_id
        self.bytes_data = bytes_data
        pub.subscribe(self.receive_message, 'send_message')
        topic = self.message_id.name.lower()
        if topic == 'send_standard' and kwargs.get('flags') and kwargs.get('flags').is_extended:
            topic = 'send_extended'
        pub.sendMessage('send.{}'.format(topic), **kwargs)

    def receive_message(self, msg):
        """Set the message from the outbound publisher."""
        self.msg = msg

    def test_id(self):
        """Test the message ID matches the expected message."""
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        """Test the byte representation matches the expected value."""
        assert bytes(self.msg) == self.bytes_data
