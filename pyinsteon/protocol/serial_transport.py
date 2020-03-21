"""Wrapper for serial.aio transport."""
import asyncio
import logging

import serial
from serial_asyncio import SerialTransport as SerialTransportBase

_LOGGER = logging.getLogger(__name__)


async def async_connect_serial(device, protocol):
    """Connect to the PowerLine Modem via serial port.

    Parameters:
        port – Device name.
        protocol - Insteon Modem Protocol instance.

    """
    loop = asyncio.get_event_loop()
    try:
        ser = serial.serial_for_url(url=device, baudrate=19200)
        transport = SerialTransport(loop, protocol, ser, device=device)
    except OSError as ex:
        _LOGGER.warning("Unable to connect to %s: %s", device, ex)
        transport = None
    return transport


async def async_connect_socket(host, protocol, port=None):
    """Connect to the Hub Version 1 via TCP Socket."""

    port = 9761 if not port else port
    loop = asyncio.get_event_loop()
    url = "socket://{}:{}".format(host, port)
    try:
        ser = serial.serial_for_url(url=url, baudrate=19200)
        transport = SerialTransport(loop, protocol, ser, device=url)
    except OSError as ex:
        _LOGGER.warning("Unable to connect to %s: %s", url, ex)
        transport = None
    return transport


class SerialTransport(SerialTransportBase):
    """Wrapper for serial_asyncio.SerialTransport."""

    def __init__(self, loop, protocol, serial_instance, device):
        """Init the SerialTransport class."""
        super().__init__(loop=loop, protocol=protocol, serial_instance=serial_instance)
        self._device = device

    @property
    def connected(self):
        """Return True if the transport is connected to the serial device."""
        return not self._closing

    def write(self, data):
        """Override SerialTransport write method."""
        msg_bytes = bytes(data)
        try:
            super().write(msg_bytes)
        except serial.SerialException:
            _LOGGER.debug("Serial connection lost (write)")
            try:
                self._close()
            except serial.SerialException as exc:
                self._serial.close()
                self._protocol.connection_lost(exc)

    async def async_write(self, data):
        """Asyncronous write method."""
        self.write(data)

    async def async_connect(self, protocol, device=None, loop=None):
        """Connect to a serial device asycrounously."""
        device = device if device else self._device
        transport = async_connect_serial(device=device, protocol=protocol)
        return transport

    def _poll_read(self):
        try:
            super()._poll_read()
        except serial.SerialException:
            _LOGGER.debug("Serial connection lost (_poll_read)")
            self._close()

    def _call_connection_lost(self, exc):
        """Override _call_connection_lost in order to capture exceptions."""
        try:
            super()._call_connection_lost(exc)
        except serial.SerialException:
            _LOGGER.debug("Serial error (_call_connection_lost)")
            protocol = self._protocol
            self._write_buffer.clear()
            self._serial.close()
            self._serial = None
            self._protocol = None
            self._loop = None
            protocol.connection_lost(exc)
