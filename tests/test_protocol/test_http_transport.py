"""Test the HTTP Transport."""

import asyncio
from binascii import unhexlify
from unittest import TestCase
from unittest.mock import patch

import pyinsteon
from pyinsteon.protocol.http_transport import HttpTransport, async_connect_http
from pyinsteon.protocol.hub_connection_exception import HubConnectionException
from pyinsteon.protocol.protocol import Protocol

from ..utils import async_case, create_mock_http_client


class MockHttpReaderWriter:
    """Mock the HttpoReaderWriter class."""

    buffer = None
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


class TestHttpTransport(TestCase):
    """Test the HTTP Reader/Writer class."""

    def setUp(self):
        """Set up the tests."""
        self.msg = None
        self.protocol = Protocol(self.mock_connection)
        self.protocol.data_received = self.data_received
        pyinsteon.protocol.http_transport.READ_WAIT = 0.05
        pyinsteon.protocol.http_transport.SESSION_RETRIES = 3
        pyinsteon.protocol.http_transport.RECONNECT_WAIT = 0.07
        self.transport = None

    def mock_connection(self):
        """Mock the transport connection method."""
        return self.transport

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
            transport = await async_connect_http(
                "host", "username", "password", self.protocol
            )
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
                "host", "username", "password", self.protocol
            )
            assert transport is None

    @async_case
    async def test_reader(self):
        """Test the reader."""
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = HttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            self.transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)

            msg_hex = "0a0b0c0d"
            MockHttpReaderWriter.buffer = msg_hex
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)

    @async_case
    async def test_reader_connection_exception(self):
        """Test the reader."""
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = HttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            MockHttpReaderWriter.read_exception_to_throw = HubConnectionException
            self.transport.start_reader()
            await asyncio.sleep(0.5)  # Sleep long enough to retry before failing
            assert self.transport.is_closing()
            assert self.msg is None

    @async_case
    async def test_reader_connection_exception_reconnect(self):
        """Test the reader."""
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = HttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            MockHttpReaderWriter.read_exception_to_throw = HubConnectionException
            self.transport.start_reader()
            await asyncio.sleep(0.1)  # Sleep long enough to fail once and try again
            assert self.msg is None
            MockHttpReaderWriter.read_exception_to_throw = None
            await asyncio.sleep(0.1)
            assert not self.transport.is_closing()
            assert self.msg == unhexlify(msg_hex)

    @async_case
    async def test_reader_generatorexit_error(self):
        """Test the reader."""
        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = HttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            MockHttpReaderWriter.read_exception_to_throw = GeneratorExit
            self.transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg is None
            assert self.transport.is_closing()

    @async_case
    async def test_pause_reader(self):
        """Test the reader."""

        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = HttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            self.transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)  # It has read correctly
            self.transport.pause_reading()
            await asyncio.sleep(0.1)
            msg_hex_new = "0a0b0c0d"
            MockHttpReaderWriter.buffer = msg_hex_new
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)  # No new message
            self.transport.resume_reading()
            await asyncio.sleep(3)
            assert self.msg == unhexlify(msg_hex_new)  # New message

    @async_case
    async def test_abort(self):
        """Test the reader."""

        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = HttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.buffer = msg_hex
            self.transport.start_reader()
            await asyncio.sleep(0.1)
            assert self.msg == unhexlify(msg_hex)  # It has read correctly
            self.transport.abort()
            await asyncio.sleep(0.1)
            assert self.transport.is_closing()

    @async_case
    async def test_writer(self):
        """Test the writer."""

        class MockHttpTransport(HttpTransport):
            """Mock HTTP Transport for testing."""

            @property
            def last_msg(self):
                """Return the last message."""
                return self._last_msg

        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = MockHttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            self.transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.1)
            assert self.transport.last_msg == unhexlify(msg_hex)

    @async_case
    async def test_writer_when_closing(self):
        """Test the writer when closing."""

        class MockHttpTransport(HttpTransport):
            """Mock HTTP Transport for testing."""

            @property
            def last_msg(self):
                """Return the last message."""
                return self._last_msg

        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = MockHttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            self.transport.close()
            self.transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.1)
            assert self.transport.last_msg is None

    @async_case
    async def test_writer_failure(self):
        """Test the writer when closing."""

        class MockHttpTransport(HttpTransport):
            """Mock HTTP Transport for testing."""

            @property
            def last_msg(self):
                """Return the last message."""
                return self._last_msg

        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = MockHttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.status = 500
            self.transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.3)
            assert self.transport.last_msg is None

    @async_case
    async def test_writer_failure_retry(self):
        """Test the writer retry on failure."""

        class MockHttpTransport(HttpTransport):
            """Mock HTTP Transport for testing."""

            @property
            def last_msg(self):
                """Return the last message."""
                return self._last_msg

        with patch.object(
            pyinsteon.protocol.http_transport,
            "HttpReaderWriter",
            MockHttpReaderWriter,
        ):
            self.transport = MockHttpTransport(
                protocol=self.protocol,
                host="host",
                username="username",
                password="password",
            )
            msg_hex = "0203040506"
            MockHttpReaderWriter.status = 500
            self.transport.write(unhexlify(msg_hex))
            await asyncio.sleep(0.1)
            MockHttpReaderWriter.status = 200
            await asyncio.sleep(0.1)
            assert self.transport.last_msg == unhexlify(msg_hex)
