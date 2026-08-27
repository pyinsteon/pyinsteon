"""Test the serial Transport."""

import asyncio
from functools import partial
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import serial

import pyinsteon
from pyinsteon.protocol.protocol import Protocol
from pyinsteon.protocol.serial_transport import (
    DEFAULT_WRITE_WAIT,
    async_connect_serial,
    async_connect_socket,
    write_wait_from_env,
)

from ..utils import MockSerial, async_case, async_protocol_manager


class MockSerialTransport(asyncio.Transport):
    """Mock the SerialTransport."""

    def __init__(self, loop, protocol, serial_instance):
        """Init the MockSerialTransport class."""
        self.poll_read_exception = None
        self.call_connection_lost_exception = None
        self.write_exception = None
        self.msg = None

    def write(self, data):
        """Mock the write method."""
        if self.write_exception:
            raise self.write_exception
        self.msg = data

    def _poll_read(self, *args, **kwargs):
        """Mock the poll_read method."""
        if self.poll_read_exception:
            raise self.poll_read_exception

    async def _call_connection_lost(self, *args, **kwargs):
        """Mock the _call_connection_lost method."""
        if self.call_connection_lost_exception:
            raise self.call_connection_lost_exception


class TestSerialTransport(TestCase):
    """Test the serial transport."""

    def setUp(self):
        """Set up the tests."""
        self.msg = None
        self.transport = None
        self.poll_read_exception = None
        self.call_connection_lost_exception = None
        self.write_exception = None
        self.msg = None

    def _write(self, data):
        """Mock the write method."""
        if self.write_exception:
            raise self.write_exception
        self.msg = data

    def _poll_read(self, *args, **kwargs):
        """Mock the poll_read method."""
        if self.poll_read_exception:
            raise self.poll_read_exception

    async def _call_connection_lost(self, *args, **kwargs):
        """Mock the _call_connection_lost method."""
        if self.call_connection_lost_exception:
            raise self.call_connection_lost_exception

    def mock_connection(self):
        """Mock the transport connection method."""
        return self.transport

    def data_received(self, data):
        """Mock the data received method."""
        self.msg = data

    async def async_create_serial_transport(
        self, method, mock_serial, device, port=None
    ):
        """Create a serial transport."""
        with (
            patch(
                "serial_asyncio_fast.SerialTransport.write",
                self._write,
            ),
            patch(
                "serial_asyncio_fast.SerialTransport._call_connection_lost",
                self._call_connection_lost,
            ),
            patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial),
        ):
            if port is not None:
                connect_method = partial(method, host=device, port=port)
            else:
                connect_method = partial(method, device=device)
        protocol = Protocol(connect_method)
        protocol.data_received = self.data_received
        return protocol

    @async_case
    async def test_connect_serial(self):
        """Test connecting to the serial device."""
        mock_serial = MockSerial()
        with (
            patch(
                "serial_asyncio_fast.SerialTransport.write",
                self._write,
            ),
            patch(
                "serial_asyncio_fast.SerialTransport._call_connection_lost",
                self._call_connection_lost,
            ),
            patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial),
        ):
            async with async_protocol_manager(
                connect_method=async_connect_serial, device="some_device"
            ) as protocol:
                assert protocol.transport.connected
                assert (
                    protocol.transport.write_wait
                    == pyinsteon.protocol.serial_transport.WRITE_WAIT
                )

    @async_case
    async def test_connect_socket(self):
        """Test connecting to the socket device."""
        mock_serial = MockSerial()
        with (
            patch(
                "serial_asyncio_fast.SerialTransport.write",
                self._write,
            ),
            patch(
                "serial_asyncio_fast.SerialTransport._call_connection_lost",
                self._call_connection_lost,
            ),
            patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial),
        ):
            async with async_protocol_manager(
                connect_method=async_connect_socket, host="some_device", port=9000
            ) as protocol:
                assert protocol.transport.connected
                assert (
                    protocol.transport.write_wait
                    == pyinsteon.protocol.serial_transport.WRITE_WAIT
                )

    @async_case
    async def test_connect_serial_exception(self):
        """Test connecting to the serial device."""
        mock_serial = MockSerial()
        mock_serial.serial_for_url_exception = OSError
        with (
            patch(
                "serial_asyncio_fast.SerialTransport.write",
                self._write,
            ),
            patch(
                "serial_asyncio_fast.SerialTransport._call_connection_lost",
                self._call_connection_lost,
            ),
            patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial),
        ):
            try:
                async with async_protocol_manager(
                    connect_method=async_connect_serial,
                    device="some_device",
                    retry=False,
                ):
                    assert False
            except ConnectionError:
                assert True

    @async_case
    async def test_connect_socket_exception(self):
        """Test connecting to the socket device."""
        mock_serial = MockSerial()
        mock_serial.serial_for_url_exception = OSError
        with (
            patch(
                "serial_asyncio_fast.SerialTransport.write",
                self._write,
            ),
            patch(
                "serial_asyncio_fast.SerialTransport._call_connection_lost",
                self._call_connection_lost,
            ),
            patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial),
        ):
            try:
                async with async_protocol_manager(
                    connect_method=async_connect_socket,
                    host="some_device",
                    port=9000,
                    retry=False,
                ):
                    assert False
            except ConnectionError:
                assert True

    @async_case
    async def test_write(self):
        """Test writing to the serial device."""
        mock_serial = MockSerial()
        with (
            patch(
                "serial_asyncio_fast.SerialTransport.write",
                self._write,
            ),
            patch(
                "serial_asyncio_fast.SerialTransport._call_connection_lost",
                self._call_connection_lost,
            ),
            patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial),
        ):
            async with async_protocol_manager(
                connect_method=async_connect_serial, device="some_device"
            ) as protocol:
                data = b"abc123"
                protocol.transport.write(data)
                await asyncio.sleep(0.05)
                assert self.msg == data

    @async_case
    async def test_write_serial_exception(self):
        """Test connecting to the socket device."""
        mock_serial = MockSerial()
        with (
            patch(
                "serial_asyncio_fast.SerialTransport.write",
                self._write,
            ),
            patch(
                "serial_asyncio_fast.SerialTransport._call_connection_lost",
                self._call_connection_lost,
            ),
            patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial),
        ):
            async with async_protocol_manager(
                connect_method=async_connect_serial, device="some_device"
            ) as protocol:
                data = b"abc123"
                mock_serial.write_exception = serial.SerialException
                protocol.connection_lost = MagicMock()
                protocol.transport.write(data)
                protocol.connection_lost.call_count == 1

    def test_write_wait_comes_from_the_environment(self):
        """PYINSTEON_WRITE_WAIT overrides the default pause between writes."""
        with patch.dict(os.environ, {"PYINSTEON_WRITE_WAIT": "0.65"}):
            assert write_wait_from_env() == 0.65

    def test_garbage_write_wait_falls_back_to_the_default(self):
        """A value that is not a number must not break the import."""
        with patch.dict(os.environ, {"PYINSTEON_WRITE_WAIT": "half a second"}):
            assert write_wait_from_env() == DEFAULT_WRITE_WAIT
