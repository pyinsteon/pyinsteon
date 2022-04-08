"""Test the serial Transport."""

import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch

import serial

import pyinsteon
from pyinsteon.protocol.protocol import Protocol
from pyinsteon.protocol.serial_transport import (
    async_connect_serial,
    async_connect_socket,
)

from ..utils import MockSerial, async_case


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

    def _call_connection_lost(self, *args, **kwargs):
        """Mock the _call_connection_lost method."""
        if self.call_connection_lost_exception:
            raise self.call_connection_lost_exception


class TestSerialTransport(TestCase):
    """Test the serial transport."""

    def setUp(self):
        """Set up the tests."""
        self.msg = None
        self.protocol = Protocol(self.mock_connection)
        self.protocol.data_received = self.data_received
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

    def _call_connection_lost(self, *args, **kwargs):
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
        with patch("serial_asyncio.SerialTransport.write", self._write,), patch(
            "serial_asyncio.SerialTransport._call_connection_lost",
            self._call_connection_lost,
        ), patch.object(pyinsteon.protocol.serial_transport, "serial", mock_serial):
            if port is not None:
                return await method(device, self.protocol, port)
            return await method(device, self.protocol)

    @async_case
    async def test_connect_serial(self):
        """Test connecting to the serial device."""
        mock_serial = MockSerial()
        transport = await self.async_create_serial_transport(
            async_connect_serial, mock_serial, "some_device"
        )
        assert transport.connected
        assert transport.write_wait == 0.8

    @async_case
    async def test_connect_socket(self):
        """Test connecting to the socket device."""
        mock_serial = MockSerial()
        transport = await self.async_create_serial_transport(
            async_connect_socket, mock_serial, "some_device", 9000
        )
        assert transport.connected
        assert transport.write_wait == 0.8

    @async_case
    async def test_connect_serial_exception(self):
        """Test connecting to the serial device."""
        mock_serial = MockSerial()
        mock_serial.serial_for_url_exception = OSError
        transport = await self.async_create_serial_transport(
            async_connect_serial, mock_serial, "some_device"
        )
        assert transport is None

    @async_case
    async def test_connect_socket_exception(self):
        """Test connecting to the socket device."""
        mock_serial = MockSerial()
        mock_serial.serial_for_url_exception = OSError
        transport = await self.async_create_serial_transport(
            async_connect_socket, mock_serial, "some_device", 9000
        )
        assert transport is None

    @async_case
    async def test_write(self):
        """Test writing to the serial device."""
        mock_serial = MockSerial()
        transport = await self.async_create_serial_transport(
            async_connect_serial, mock_serial, "some_device"
        )
        data = b"abc123"
        transport.write(data)
        await asyncio.sleep(0.05)
        assert mock_serial.msg == data

    @async_case
    async def test_write_serial_exception(self):
        """Test connecting to the socket device."""
        mock_serial = MockSerial()
        transport = await self.async_create_serial_transport(
            async_connect_serial, mock_serial, "some_device"
        )
        data = b"abc123"
        mock_serial.write_exception = serial.SerialException
        self.protocol.connection_lost = MagicMock()
        transport.write(data)
        self.protocol.connection_lost.call_count == 1
