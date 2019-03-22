"""Serial protocol to perform async I/O with the Powerline Modem (PLM)."""

import asyncio
import logging
from enum import Enum

from serial_asyncio import create_serial_connection

from .. import pub
from .msg_to_topic import convert_to_topic
from .messages.inbound import create

_LOGGER = logging.getLogger(__name__)
WRITE_WAIT = 1.5  # Time to wait between writes to transport


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
                                                         device,
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

    def __init__(self, *args, **kwargs):
        """Init the SerialProtocol class."""
        super().__init__(*args, **kwargs)
        self._transport = None
        self._status = TransportStatus.CLOSED
        self._message_queue = asyncio.PriorityQueue()
        self._buffer = bytearray()
        self._writer_task = None

    @property
    def connected(self) -> bool:
        """Return true if the transport is connected."""
        return self._status in [TransportStatus.OPEN, TransportStatus.PAUSED]

    def connection_made(self, transport):
        self._transport = transport
        self._start_writer()
        self._subscribe()
        self._status = TransportStatus.OPEN
        pub.sendMessage('connection.made')

    def data_received(self, data):
        """Receive data from the serial transport."""
        self._buffer.extend(data)
        _LOGGER.debug('CURR BUFF: %s', self._buffer.hex())
        while True:
            last_buffer = self._buffer
            _LOGGER.debug('BUFFER IN: %s', self._buffer.hex())
            msg, self._buffer = create(self._buffer)
            _LOGGER.debug('BUFFER OUT: %s', self._buffer.hex())
            if msg:
                (topic, kwargs) = convert_to_topic(msg)
                if self._is_nak(msg) and not self._has_listeners(topic):
                    self._resend(msg)
                else:
                    pub.sendMessage(topic, **kwargs)
            if last_buffer == self._buffer or not self._buffer:
                _LOGGER.debug('BREAKING: %s', self._buffer.hex())
                break

    def connection_lost(self, exc):
        """Notify listeners that the serial connection is lost."""
        self._writer_task.cancel()
        self._status = TransportStatus.CLOSED
        pub.sendMessage('connection.lost')

    def pause_writing(self):
        """Pause writing to the transport."""
        self._writer_task.cancel()
        self._status = TransportStatus.PAUSED
        pub.sendMessage('protocol.writing.pause')

    def resume_writing(self):
        """Resume writing to the transport."""
        self._start_writer()
        self._status = TransportStatus.OPEN
        pub.sendMessage('protocol.writing.resume')

    def close(self):
        """Close the serial transport."""
        self._unsubscribe()
        if self._transport:
            self._transport.close()
        self._writer_task.cancel()
        self._status = TransportStatus.CLOSED

    def _write(self, msg, priority=5):
        """Prepare data for writing to the transport.

        Data is actually writen by _write_message to ensure a pause beteen writes.
        This approach minimizes NAK messages. This also allows for some messages
        to be lower priority such as 'Load ALDB' versus higher priority such as
        'Set Light Level'.
        """
        send_msg = msg if isinstance(msg, bytes) else bytes(msg)
        self._message_queue.put_nowait((priority, send_msg))

    def _subscribe(self):
        """Subscribe to topics."""
        pub.subscribe(self._write, "send")

    def _resend(self, msg):
        """Resend after a NAK message.

        TODO: Avoid resending the same message 10 times.
        """
        self._write(bytes(msg)[:-1])

    def _is_nak(self, msg):
        """Test if a message is a NAK from the modem."""
        if hasattr(msg, 'ack') and msg.ack.value == 0x15:
            return True
        return False

    def _has_listeners(self, topic):
        """Test if a topic has listeners.

        Only used if the msg is a NAK. If no NAK specific listeners
        then resend the message. Otherwise it is assumed the NAK
        specific listner is resending if necessary.
        """
        topicManager = pub.getDefaultTopicMgr()
        pub_topic = topicManager.getTopic(name=topic, okIfNone=True)
        if pub_topic and pub_topic.getListeners():
            return True
        return False

    def _unsubscribe(self):
        """Unsubscribe to topics."""
        pub.unsubscribe(self._write, 'send')

    def _start_writer(self):
        """Start the message writer."""
        self._writer_task = asyncio.ensure_future(self._write_messages())

    async def _write_messages(self):
        """Write data to the transport."""
        while self._status == TransportStatus.OPEN:
            _, msg = await self._message_queue.get()
            self._transport.write(msg)
            await asyncio.sleep(WRITE_WAIT)
