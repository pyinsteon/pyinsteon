"""Serial protocol to perform async I/O with the Insteon Modem."""

import asyncio
import logging
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


def _get_addresses_in_msg(msg):
    """Return a list of addresses included in a message."""
    addresses = []
    addr_fields = ["address", "target"]
    for fld in addr_fields:
        try:
            addr = getattr(msg, fld)
        except AttributeError:
            continue
        else:
            if addr not in addresses:
                addresses.append(addr)
    return addresses


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
        self._writer_lock = asyncio.Lock()
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
        publish_topic("connection.made")

    def data_received(self, data):
        """Receive data from the serial transport."""
        self._buffer.extend(data)
        while True:
            last_buffer = self._buffer
            try:
                msg, self._buffer = create(self._buffer)
            except (ValueError, IndexError) as ex:
                _LOGGER.debug("Invalid message data: %s", self._buffer.hex())
                _LOGGER.debug("%s: %s", type(ex), str(ex))
                self._buffer = self._buffer[1:]
                msg = None

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
                asyncio.create_task(self._publish_message(msg))
                msg = None

            if not self._buffer or last_buffer == self._buffer:
                break

    def connection_lost(self, exc: asyncio.Task):
        """Notify listeners that the serial connection is lost."""
        _LOGGER.debug("Connection lost called")
        _LOGGER.debug("Should reconnect: %s", self._should_reconnect)
        if exc and exc.exception():
            _LOGGER.warning("pyinsteon transport exception: %s", str(exc.exception()))
        if self._should_reconnect:
            asyncio.create_task(self.async_connect())
        else:
            asyncio.create_task(self._stop_writer())

    async def async_connect(self, retry=True):
        """Connect to the transport asynchronously."""
        wait_time = 0.1
        await asyncio.sleep(0.5)  # Give everything time to settle
        while not self.connected:
            _LOGGER.debug("Attempting to connect to modem")
            self._transport = await self._connect_method(protocol=self)
            if self._transport is None and not retry:
                publish_topic("connection.failed")
                raise ConnectionError("Modem did not respond to connection request")
            await asyncio.sleep(0.1)  # Let the transport finish connecting
            if not self.connected and retry:
                await asyncio.sleep(wait_time)
                wait_time = min(MAX_RECONNECT_WAIT_TIME, 1.5 * wait_time)
        if not self._writer_lock.locked():
            self._start_writer()

        _LOGGER.debug("Connected to modem in async_connect")

    def pause_writing(self):
        """Pause writing to the transport."""
        asyncio.ensure_future(self._stop_writer())

    def resume_writing(self):
        """Resume writing to the transport."""
        self._start_writer()

    def close(self):
        """Close the serial transport."""
        self._should_reconnect = False
        asyncio.ensure_future(self._stop_writer())
        if self._transport:
            self._transport.close()

    def _start_writer(self, *args, **kwargs):
        """Start the message writer."""
        if self._transport and not self._transport.is_closing():
            _LOGGER.debug("Scheduling the writer")
            while not self._message_queue.empty():
                self._message_queue.get_nowait()
            self._writer_task = asyncio.create_task(self._write_messages())
            self._writer_task.add_done_callback(self._start_writer)
        else:
            _LOGGER.debug("Did not schedule the writer since we are closing")

    async def _stop_writer(self):
        """Stop the writer task."""
        if self._writer_task:
            self._writer_task.remove_done_callback(self._start_writer)
        await self._message_queue.put((0, None))

    # pylint: disable=broad-except
    async def _publish_message(self, msg):
        """Convert an inbound message to a topic and publish to listeners."""
        _LOGGER_MSG.debug("RX: %s", repr(msg))
        if _LOGGER_MSG.level == 0 or _LOGGER_MSG.level > logging.DEBUG:
            for addr in _get_addresses_in_msg(msg):
                logger = logging.getLogger(f"pyinsteon.{addr.id}")
                logger.debug("RX: %s", repr(msg))
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

        Data is actually written by _write_message to ensure a pause between writes.
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
        await asyncio.sleep(0.1)
        if self._writer_lock.locked():
            _LOGGER.debug("Writer still running")
            return

        async with self._writer_lock:
            _LOGGER.debug("Modem writer started.")
            try:
                while self._transport and not self._transport.is_closing():
                    _, msg = await self._message_queue.get()
                    if msg is None:
                        return
                    _LOGGER_MSG.debug("TX: %s", repr(msg))
                    if _LOGGER_MSG.level == 0 or _LOGGER_MSG.level > logging.DEBUG:
                        for addr in _get_addresses_in_msg(msg):
                            logger = logging.getLogger(f"pyinsteon.{addr.id}")
                            logger.debug("TX: %s", repr(msg))
                    while not self._last_message.empty():
                        self._last_message.get()
                    self._last_message.put(msg)
                    await self._transport.async_write(msg)
                    await asyncio.sleep(self._transport.write_wait)
            except RuntimeError as error:
                _LOGGER.warning(
                    "Modem writer stopped due to a runtime error: %s", str(error)
                )
        _LOGGER.debug("Modem writer stopped.")
