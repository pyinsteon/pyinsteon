"""Serial protocol to perform async I/O with the Powerline Modem (PLM)."""

import asyncio
import logging
from enum import Enum

from serial_asyncio import SerialTransport, create_serial_connection

from .. import pub
from .topics import convert_to_topic
from ..messages.inbound import create

_LOGGER = logging.getLogger(__name__)
WRITE_WAIT = 1.5  # Time to wait between writes to transport


@classmethod
async def connect(device, loop=None, baudrate=19200, **kwargs):
    """Connect to the serial port.

    Parameters:

    port – Device name.

    baudrate (int) – Baud rate such as 9600 or 115200 etc.

    bytesize – Number of data bits. Possible values: FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS

    parity – Enable parity checking. Possible values: PARITY_NONE, PARITY_EVEN, PARITY_ODD
    PARITY_MARK, PARITY_SPACE

    stopbits – Number of stop bits. Possible values: STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE,
    STOPBITS_TWO

    timeout (float) – Set a read timeout value.

    xonxoff (bool) – Enable software flow control.

    rtscts (bool) – Enable hardware (RTS/CTS) flow control.

    dsrdtr (bool) – Enable hardware (DSR/DTR) flow control.

    write_timeout (float) – Set a write timeout value.

    inter_byte_timeout (float) – Inter-character timeout, None to disable (default).
    """
    loop = loop if loop else asyncio.get_event_loop()
    transport, protocol = await create_serial_connection(loop, SerialProtocol,
                                                         port=device,
                                                         baudrate=baudrate,
                                                         **kwargs)
    return transport, protocol


class TransportStatus(Enum):
    """Status of the transport."""

    CLOSED = 0
    LOST = 1
    PAUSED = 2
    OPEN = 3


class SerialProtocol(asyncio.Protocol):
    """Serial protocol to perform async I/O with the PLM."""

    _loop = asyncio.get_event_loop()
    _transport: SerialTransport
    _device = None
    _status = TransportStatus.CLOSED
    _write_lock = asyncio.Lock()
    _message_queue = asyncio.PriorityQueue()
    _buffer = []

    def connection_made(self, transport):
        self._status = TransportStatus.OPEN
        self._subscribe()
        self._transport = transport
        self._start_writer()
        pub.sendMessage('protocol.connection.made')

    def data_received(self, data):
        """Receive data from the serial transport."""
        self._buffer.append(data)
        self._buffer, msg = create(self._buffer)
        if msg:
            (topic, kwargs) = convert_to_topic(msg)
            pub.sendMessage(topic, **kwargs)

    def connection_lost(self, exc):
        """Notify listeners that the serial connection is lost."""
        self._status = TransportStatus.CLOSED
        pub.sendMessage('protocol.connection.lost')

    def pause_writing(self):
        """Pause writing to the transport."""
        self._status = TransportStatus.PAUSED
        asyncio.ensure_future(self._write_lock.acquire())
        pub.sendMessage('protocol.writing.pause')

    def resume_writing(self):
        """Resume writing to the transport."""
        self._status = TransportStatus.OPEN
        self._start_writer()
        pub.sendMessage('protocol.writing.resume')

    async def _write(self, data, priority=5):
        """Prepare data for writing to the transport.

        Data is actually writen by _write_message to ensure a pause beteen writes.
        This approach minimizes NAK messages. This also allows for some messages
        to be lower priority such as 'Load ALDB' versus higher priority such as
        'Set Light Level'.
        """
        msg = data if isinstance(data, bytes) else bytes(data)
        self._message_queue.put_nowait((priority, msg))

    def _subscribe(self):
        """Subscribe to topics."""
        pub.subscribe(self._write, "protocol.send")

    def _unsubscribe(self):
        """Unsubscribe to topics."""
        pub.unsubscribe(self._write, 'protocol.send')

    def _start_writer(self):
        """Start the message writer."""
        asyncio.ensure_future(self._write_messages())

    async def _write_messages(self):
        """Write data to the transport."""
        while self._status == TransportStatus.OPEN:
            _, msg = await self._message_queue.get()
            self._transport.write(msg)
            await asyncio.sleep(WRITE_WAIT)
