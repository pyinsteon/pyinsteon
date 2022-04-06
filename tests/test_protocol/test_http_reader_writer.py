"""Test the HTTP Reader/Writer class."""
from unittest import TestCase

import aiohttp

from pyinsteon.protocol.http_reader_writer import HttpReaderWriter

from ..utils import async_case

# from unittest.mock import AsyncMock, patch


class TestHttpReaderWriter(TestCase):
    """Test the HTTP Reader/Writer class."""

    def setUp(self):
        """Set up the tests."""
        self._auth = aiohttp.BasicAuth("username", "password")
        self.http_rw = HttpReaderWriter(self._auth)

    @async_case
    async def test_test_connection(self):
        """Test the test connection method."""

        # with patch.object()
