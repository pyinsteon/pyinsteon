"""Wrapper for serial.aio transport."""
from serial_asyncio import SerialTransport as SerialTransportBase
from serial import SerialException


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
        except SerialException as exc:
            self._protocol.connection_lost(exc)

    async def async_write(self, data):
        """Asyncronous write method."""
        self.write(data)

    async def async_connect(self, protocol, device=None, loop=None):
        """Connect to a serial device asycrounously."""
        from . import async_connect_serial

        device = device if device else self._device
        transport = async_connect_serial(device=device, protocol=protocol)
        return transport

    def _poll_read(self):
        try:
            super()._poll_read()
        except SerialException as exc:
            self._protocol.connection_lost(exc)
