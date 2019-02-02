"""Base class for testing templates."""

import logging
import unittest
import sys

from ...utils import check_fields_match

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestTemplateBase():

    def setup(self):
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        _INSTEON_LOGGER.addHandler(stream_handler)

    def test_id(self):
        assert self.msg.message_id == self.message_id

    def test_fields_match(self):
        assert check_fields_match(self.msg_in, self.msg)
