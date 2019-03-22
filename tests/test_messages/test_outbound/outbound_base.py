"""Base class for testing outbound messages."""

import logging
import unittest
import sys

from tests.utils import check_fields_match


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


stream_handler = logging.StreamHandler(sys.stdout)
_LOGGER.addHandler(stream_handler)
_INSTEON_LOGGER.addHandler(stream_handler)


class TestOutboundBase():

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_bytes(self):
        assert bytes(self.msg) == self.bytes_data
