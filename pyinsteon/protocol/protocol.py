"""Serial protocol to perform async I/O with the Insteon Modem."""

import asyncio
import logging
from contextlib import suppress
from enum import Enum
from queue import SimpleQueue

from .. import pub
from ..constants import AckNak
from ..utils import log_error, publish_topic
from .command_to_msg import register_command_handlers
from .messages.inbound import create
from .messages.outbound import outbound_write_manager, register_outbound_handlers
from .msg_to_topic import convert_to_topic

_LOGGER = logging.getLogger(__name__)
_LOGGER_MSG = logging.getLogger("pyinsteon.messages")
MAX_RECONNECT_WAIT_TIME = 300


def _is_nak(msg):
    """Test if a message is a NAK from the modem."""
    if hasattr(msg, "ack") and msg.ack.value == 0x15:
        return True
    return False


def _has_listeners(topic):
    """Test if a topic has listeners.

    Only used if the msg is a NAK. If no NAK specific listeners
    then resend the message. Otherwise it is assumed the NAK
    specific listner is resending if necessary.
    """
    topic_manager = pub.getDefaultTopicMgr()
    pub_topic = topic_manager.getTopic(name=topic, okIfNone=True)
    _LOGGER.debug("MSG Topic: %s", pub_topic)
    if pub_topic and pub_topic.getListeners():
        _LOGGER.debug("Has listeners so do not resend.")
        return True
    _LOGGER.debug("No listeners so resend")
    return False


class TransportStatus(Enum):
    """Status of the transport."""

    CLOSED = 0
    LOST = 1
    PAUSED = 2
    OPEN = 3


class Protocol(asyncio.Protocol):
    """Serial protocol to perform async I/O with the PLM."""

    def __init__(self, connect_method, *args, **kwargs):
        """Init the SerialProtocol class."""
        super().__init__(*args, **kwargs)
        self._transport = None
        self._message_queue = asyncio.PriorityQueue()
        self._last_message = SimpleQueue()
        self._buffer = bytearray()
        self._should_reconnect = True
        self._connect_method = connect_method
        self._writer_task = None
        outbound_write_manager.protocol_write = self.write
        register_outbound_handlers()
        register_command_handlers()

    @property
    def connected(self) -> bool:
        """Return true if the transport is connected."""
        return not self._transport.is_closing() if self._transport else False

    @property
    def message_queue(self):
        """Return the queue of messages to write to the transport."""
        return self._message_queue

    @property
    def transport(self):
        """Return the transport."""
        return self._transport
    
    def connection_made(self, transport):
        """Run when a connection to the transport has been made."""
        self._transport = transport
        self._start_writer()
        publish_topic("connection.made")

    def data_received(self, data):
        """Receive data from the serial transport."""
        self._buffer.extend(data)
        while True:
            last_buffer = self._buffer
            msg, self._buffer = create(self._buffer)

            # Sometimes the modem only responds with NAK and not the original message
            if (
                not msg
                and last_buffer
                and last_buffer[-1] == AckNak.NAK
                and not self._last_message.empty()
            ):
                last_msg = self._last_message.get()
                last_msg_nak = bytearray(bytes(last_msg))
                last_msg_nak.extend(bytes([0x15]))
                msg, _ = create(last_msg_nak)
            if msg:
                asyncio.ensure_future(self._publish_message(msg))
                msg = None

            if not self._buffer or last_buffer == self._buffer:
                break

    def connection_lost(self, exc):
        """Notify listeners that the serial connection is lost."""
        _LOGGER.debug("Connection lost called")
        _LOGGER.debug("Should reconnect: %s", self._should_reconnect)
        asyncio.ensure_future(self._async_stop_writer())
        if self._should_reconnect:
            asyncio.ensure_future(self.async_connect())

    async def async_connect(self, retry=True):
        """Connect to the transport asyncrously."""
        wait_time = 0.1
        while not self.connected:
            self._transport = await self._connect_method(protocol=self)
            if self._transport is None and not retry:
                publish_topic("connection.failed")
                raise ConnectionError("Modem did not respond to connection request")
            if not self.connected and retry:
                await asyncio.sleep(wait_time)
                wait_time = min(MAX_RECONNECT_WAIT_TIME, 1.5 * wait_time)

    def pause_writing(self):
        """Pause writing to the transport."""
        asyncio.ensure_future(self._async_stop_writer())

    def resume_writing(self):
        """Resume writing to the transport."""
        self._start_writer()

    def close(self):
        """Close the serial transport."""
        self._should_reconnect = False
        asyncio.ensure_future(self._async_stop_writer())
        if self._transport:
            self._transport.close()

    def _start_writer(self, *args, **kwargs):
        """Start the message writer."""
        if not self._transport.is_closing():
            self._writer_task = asyncio.ensure_future(self._write_messages())
            self._writer_task.add_done_callback(self._start_writer)

    async def _async_stop_writer(self):
        """Stop the writer task."""
        if self._writer_task:
            self._writer_task.remove_done_callback(self._start_writer)
            self._writer_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._writer_task
            await asyncio.sleep(0.01)
            self._writer_task = None

    # pylint: disable=broad-except
    async def _publish_message(self, msg):
        """Convert an inbound message to a topic and publish to listeners."""
        _LOGGER_MSG.debug("RX: %s", repr(msg))
        topic = None
        kwargs = {}
        try:
            for (topic, kwargs) in convert_to_topic(msg):
                if _is_nak(msg) and not _has_listeners(topic):
                    self._resend(msg)
                else:
                    publish_topic(topic, **kwargs)
        except ValueError:
            # No topic was found for this message
            _LOGGER.debug("No topic found for message %r", msg)
        except Exception as ex:
            log_error(msg, ex, topic=topic, kwargs=kwargs)

    def write(self, msg, priority=5):
        """Prepare data for writing to the transport.

        Data is actually writen by _write_message to ensure a pause beteen writes.
        This approach minimizes NAK messages. This also allows for some messages
        to be lower priority such as 'Load ALDB' versus higher priority such as
        'Set Light Level'.
        """
        self._message_queue.put_nowait((priority, msg))

    def _resend(self, msg):
        """Resend after a NAK message.

        TODO: Avoid resending the same message 10 times.
        """
        self.write(bytes(msg)[:-1])

    async def _write_messages(self):
        """Write data to the transport."""
        _LOGGER.debug("Modem writer started.")
        while not self._transport.is_closing():
            _, msg = await self._message_queue.get()
            _LOGGER_MSG.debug("TX: %s", repr(msg))
            while not self._last_message.empty():
                self._last_message.get()
            self._last_message.put(msg)
            await self._transport.async_write(msg)
            await asyncio.sleep(self._transport.write_wait)
        _LOGGER.debug("Modem writer stopped.")
