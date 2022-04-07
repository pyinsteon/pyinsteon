"""Test the HTTP Transport."""

import asyncio
import aiofiles
import json
from aiohttp.client_exceptions import ClientError
from unittest import TestCase
from unittest.mock import MagicMock, patch
from contextlib import asynccontextmanager
from functools import partial

import pyinsteon
from pyinsteon.protocol.protocol import Protocol
from pyinsteon.protocol.http_transport import async_connect_http, HttpTransport

from ..utils import async_case, create_mock_http_client


class TestHttpTransport(TestCase):
    """Test the HTTP Reader/Writer class."""

    def setUp(self):
        """Set up the tests"""
        self.msg = None

    def data_received(self, data):
        """Mock the data received method."""
        self.msg = data

    @async_case
    async def test_async_connect_http(self):
        """Test the test connection method success."""

        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            create_mock_http_client,
        ):
            protocol = Protocol(None)
            transport = await async_connect_http(
                "host", "username", "password", protocol
            )
            assert isinstance(transport, HttpTransport)
            assert not transport.can_write_eof()
            assert not transport.is_closing()
            try:
                transport.set_write_buffer_limits()
                assert False
            except NotImplementedError:
                assert True

    @async_case
    async def test_reader(self):
        """Test the reader."""

        async def mock_async_read(*args, **kwargs):
            """Mock the async_read method."""
            return "Message"

        async def mock_async_write(*args, **kwargs):
            """Mock the async_read method."""
            return 200

        async def mock_reset_reader(*args, **kwargs):
            """Mock the reset_reader method."""

        save_transport = []

        mock_reader_writer = MagicMock()
        mock_reader_writer.async_read = mock_async_read
        mock_reader_writer.async_write = MagicMock(return_value=mock_async_write)
        mock_reader_writer.reset_reader = mock_reset_reader

        async def mock_connection(protocol):
            return save_transport[0]

        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            mock_reader_writer,
        ):
            protocol = Protocol(mock_connection)
            transport = HttpTransport(
                protocol=protocol, host="host", username="username", password="password"
            )
            save_transport.append(transport)
            protocol.data_received = self.data_received
            await asyncio.sleep(0.1)
            transport.start_reader()
            await asyncio.sleep(800)
            assert self.msg
