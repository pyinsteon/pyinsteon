"""Test the HTTP Transport."""

import asyncio
from binascii import unhexlify
from unittest import TestCase
from unittest.mock import patch

import pyinsteon
from pyinsteon.protocol.http_transport import HttpTransport, async_connect_http
from pyinsteon.protocol.hub_connection_exception import HubConnectionException

from ..utils import async_case, create_mock_http_client

TEST_LOCK = asyncio.Lock()


class MockProtocol:
    """Mock protocol object."""

    def connection_made(self, *args, **kwargs):
        """Mock the connection made method."""

    def connection_lost(self, *args, **kwargs):
        """Mock the connection lost method."""

    def data_received(self, *args, **kwargs):
        """Mock the data received method."""


class MockHttpReaderWriter:
    """Mock the HttpoReaderWriter class."""

    buffer = "0" * 202
    read_exception_to_throw = None
    write_exception_to_throw = None
    test_connection = True
    status = 200

    def __init__(self, *arg, **kwargs):
        """Init the MockHttpReaderWriter class."""

    async def async_read(self, url):
        """Mock the async_read method."""
        if self.read_exception_to_throw is not None:
            raise self.read_exception_to_throw
        return self.buffer

    async def async_write(self, url):
        """Mock the async_write method."""
        if self.write_exception_to_throw is not None:
            raise self.write_exception_to_throw
        return self.status

    async def reset_reader(self):
        """Mock the reset reader method."""

    async def async_test_connection(self, url):
        """Mock the test_connection method."""
        return self.test_connection


class MockHttpTransport(HttpTransport):
    """Mock HTTP Transport for testing."""

    @property
    def last_msg(self):
        """Return the last message."""
        return self._last_msg


async def mock_async_connect_http(host, username, password, protocol, port=None):
    """Connect to the Hub Version 2 via HTTP."""
    port = 25105 if not port else port
    transport = MockHttpTransport(
        protocol=protocol, host=host, port=port, username=username, password=password
    )
    if await transport.async_test_connection():
        transport.start_reader()
        protocol.connection_made(transport)
        return transport
    return None


class TestHttpTransport(TestCase):
    """Test the HTTP Reader/Writer class."""

    def setUp(self):
        """Set up the tests."""
        self.msg = None
        pyinsteon.protocol.http_transport.READ_WAIT = 0.05
        pyinsteon.protocol.http_transport.SESSION_RETRIES = 3
        pyinsteon.protocol.http_transport.RECONNECT_WAIT = 0.07
        MockHttpReaderWriter.buffer = "0" * 202
        MockHttpReaderWriter.read_exception_to_throw = None
        MockHttpReaderWriter.write_exception_to_throw = None
        MockHttpReaderWriter.test_connection = True
        MockHttpReaderWriter.status = 200

    def data_received(self, data):
        """Mock the data received method."""
        self.msg = data

    @async_case
    async def test_async_connect_http(self):
        """Test the test connection method success."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_reader_writer,
            "ClientSession",
            create_mock_http_client,
        ), patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            await asyncio.sleep(0.1)
            assert isinstance(transport, HttpTransport)
            assert not transport.can_write_eof()
            assert not transport.is_closing()
            assert transport.write_wait == 0.5
            assert transport.get_write_buffer_size() == 0
            try:
                transport.set_write_buffer_limits()
                assert False
            except NotImplementedError:
                assert True
            try:
                transport.write_eof()
                assert False
            except NotImplementedError:
                assert True
            try:
                transport.writelines("some line")
                assert False
            except NotImplementedError:
                assert True

    @async_case
    async def test_async_connect_http_failed(self):
        """Test the test connection method failure."""
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            MockHttpReaderWriter.test_connection = False
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=None,
            )
            assert transport is None

    @async_case
    async def test_async_reader(self):
        """Test the reader."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)

            msg_hex = "0a0b0c0d"
            MockHttpReaderWriter.buffer = msg_hex
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)

    @async_case
    async def test_reader_connection_exception(self):
        """Test the reader connection exception."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            MockHttpReaderWriter.read_exception_to_throw = HubConnectionException
            transport.start_reader()
            await asyncio.sleep(0.5)  # Sleep long enough to retry before failing
            assert transport.is_closing()
            assert self.msg is None

    @async_case
    async def test_reader_connection_exception_reconnect(self):
        """Test the reader connection exception reconnect."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            MockHttpReaderWriter.read_exception_to_throw = HubConnectionException
            transport.start_reader()
            await asyncio.sleep(0.1)  # Sleep long enough to fail once
            assert self.msg is None
            MockHttpReaderWriter.read_exception_to_throw = None
            await asyncio.sleep(0.1)  # Sleep long enough to read again
            assert not transport.is_closing()
            assert self.msg == unhexlify(msg_hex)

    @async_case
    async def test_reader_generatorexit_error(self):
        """Test the reader generatorexit error."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            MockHttpReaderWriter.read_exception_to_throw = GeneratorExit
            transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg is None
            assert transport.is_closing()

    @async_case
    async def test_async_pause_reader(self):
        """Test pause reader."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)  # It has read correctly
            transport.pause_reading()
            await asyncio.sleep(0.1)
            msg_hex_new = "0a0b0c0d"
            MockHttpReaderWriter.buffer = msg_hex_new
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)  # No new message
            transport.resume_reading()
            await asyncio.sleep(0.3)
            assert self.msg == unhexlify(msg_hex_new)  # New message

    @async_case
    async def test_abort(self):
        """Test abort."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)  # It has read correctly
            transport.abort()
            await asyncio.sleep(0.1)
            assert transport.is_closing()

    @async_case
    async def test_writer(self):
        """Test the writer."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await mock_async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.1)
            assert transport.last_msg == unhexlify(msg_hex)

    @async_case
    async def test_writer_when_closing(self):
        """Test the writer when closing."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await mock_async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            transport.close()
            transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.1)
            assert transport.last_msg is None

    @async_case
    async def test_writer_failure(self):
        """Test the writer when failure."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await mock_async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.status = 500
            transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.1)
            assert transport.last_msg is None

    @async_case
    async def test_writer_failure_retry(self):
        """Test the writer retry on failure."""
        mock_protocol = MockProtocol()
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            transport = await mock_async_connect_http(
                host="host",
                username="username",
                password="password",
                protocol=mock_protocol,
            )
            mock_protocol.data_received = self.data_received
            msg_hex = "0203040506"
            MockHttpReaderWriter.status = 500
            transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.1)
            assert transport.last_msg is None
            await asyncio.sleep(0.1)
            MockHttpReaderWriter.status = 200
            await asyncio.sleep(0.3)
            assert transport.last_msg == unhexlify(msg_hex)
