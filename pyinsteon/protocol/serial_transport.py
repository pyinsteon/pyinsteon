"""Wrapper for serial.aio transport."""
import asyncio
import logging

import serial
from serial_asyncio import SerialTransport

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
        transport = SerialTransportInsteon(loop, protocol, ser, device=device)
    except OSError as ex:
        _LOGGER.warning("Unable to connect to %s: %s", device, ex)
        transport = None
    return transport


async def async_connect_socket(host, protocol, port=None):
    """Connect to the Hub Version 1 via TCP Socket."""

    port = 9761 if not port else port
    loop = asyncio.get_event_loop()
    url = f"socket://{host}:{port}"
    try:
        ser = serial.serial_for_url(url=url, baudrate=19200)
        transport = SerialTransportInsteon(loop, protocol, ser, device=url)
    except OSError as ex:
        _LOGGER.warning("Unable to connect to %s: %s", url, ex)
        transport = None
    return transport


class SerialTransportInsteon(SerialTransport):
    """Wrapper for serial_asyncio.SerialTransport."""

    def __init__(self, loop, protocol, serial_instance, device):
        """Init the SerialTransportInsteon class."""
        super().__init__(loop=loop, protocol=protocol, serial_instance=serial_instance)
        self._device = device

    @property
    def connected(self):
        """Return True if the transport is connected to the serial device."""
        return not self._closing

    @property
    def write_wait(self):
        """Return the time to wait between writes."""
        return 0.8

    def write(self, data):
        """Override SerialTransport write method."""
        msg_bytes = bytes(data)
        super().write(msg_bytes)

    async def async_write(self, data):
        """Asyncronous write method."""
        self.write(data)
