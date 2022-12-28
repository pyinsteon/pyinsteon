"""Mock transport for test purposes."""
import asyncio
from binascii import Error, Incomplete, unhexlify
import logging

from ...address import Address
from ...constants import AckNak, MessageFlagType, MessageId
from ...data_types.message_flags import MessageFlags
from .mock_reader import MockReader

_LOGGER = logging.getLogger(__name__)
READ_WAIT = 0.5
SESSION_RETRIES = 30
RECONNECT_WAIT = 7


HOST = "127.0.0.1"
PORT = 8080
MODEM_ADDRESS = Address("11.11.11")


def _create_direct_ack(msg):
    """Create a DIRECT ACK response to a standard or extended outbound message."""
    msg_flag = MessageFlags.create(MessageFlagType.DIRECT_ACK, False)
    addr = msg.address
    cmd1 = msg.cmd1
    cmd2 = msg.cmd2
    dir_ack = bytearray([0x02, int(MessageId.STANDARD_RECEIVED)])
    dir_ack.extend(bytes(addr))
    dir_ack.extend(bytes(MODEM_ADDRESS))
    dir_ack.extend(bytes(msg_flag))
    dir_ack.extend(bytearray([cmd1, cmd2]))
    return dir_ack


async def async_connect_mock(protocol, host=None, port=None):
    """Connect to a mock transport."""
    host = HOST if not host else host
    port = PORT if not port else port
    transport = MockTransport(protocol=protocol, host=host, port=port)
    if await transport.async_test_connection():
        _LOGGER.debug("Connection made async_connect_mock")
        transport.start_reader()
        protocol.connection_made(transport)
        return transport
    return None


# This transport is designed for the Hub version 2.
# Hub version 1 should use socket interface on port 9761.
# pylint: disable=too-many-instance-attributes
class MockTransport(asyncio.Transport):
    """An asyncio transport model of a mock communication channel.

    A transport class is an abstraction of a communication channel.
    This allows protocol implementations to be developed against the
    transport abstraction without needing to know the details of the
    underlying channel, such as whether it is a pipe, a socket, or
    indeed an HTTP connection.


    You generally won’t instantiate a transport yourself; instead, you
    will call `async_connect_mock` which will create the
    transport and try to initiate the underlying communication channel,
    calling you back when it succeeds.
    """

    def __init__(self, protocol, host="127.0.0.1", port=8080):
        """Init the HttpTransport class."""
        super().__init__()
        self._protocol = protocol
        self._host = host
        self._port = port
        self._webserver = MockReader(host, port)

        self._closing = False
        self._reader_lock = asyncio.Lock()
        self._read_write_lock = asyncio.Lock()
        self._last_read = asyncio.Queue()
        self._last_msg = None
        self._reader_task = None

    @property
    def write_wait(self):
        """Return the time to wait between writes."""
        return 0.05

    def abort(self):
        """Alternative to closing the transport."""
        self.close()

    def can_write_eof(self):
        """Return False always."""
        return False

    def is_closing(self):
        """Return the state of the transport.

        True if the transport is closed or in the process of closing.

        """
        return self._closing

    def close(self):
        """Close the transport."""
        _LOGGER.debug("Closing Hub session")
        self._closing = True
        self._webserver.stop()

    def get_write_buffer_size(self):
        """Rreturn 0 (i.e. none) always."""
        return 0

    def pause_reading(self):
        """Pause the read."""
        asyncio.ensure_future(self._stop_reader(False))

    def resume_reading(self):
        """Resume the reader."""
        self.start_reader()

    def set_write_buffer_limits(self, high=None, low=None):
        """Not implemented."""
        raise NotImplementedError("HTTP connections do not support write buffer limits")

    def write(self, data):
        """Write data to the transport."""
        asyncio.ensure_future(self.async_write(data))

    async def async_write(self, data):
        """Async write to the transport."""
        await asyncio.sleep(0.01)
        if data.message_id == MessageId.GET_IM_INFO:
            ack_response = bytearray([0x02, int(MessageId.GET_IM_INFO)])
            ack_response.extend(bytearray(bytes(MODEM_ADDRESS)))
            ack_response.append(0x03)
            ack_response.append(0x00)
            ack_response.append(0x00)
            ack_response.append(int(AckNak.ACK))
        elif data.message_id == MessageId.GET_IM_CONFIGURATION:
            ack_response = bytearray(
                [
                    0x02,
                    int(MessageId.GET_IM_CONFIGURATION),
                    0x00,
                    0x00,
                    0x00,
                    AckNak.ACK,
                ]
            )
        else:
            ack_response = bytes(data) + bytes([int(AckNak.ACK)])
        self._protocol.data_received(bytes(ack_response))
        await asyncio.sleep(0.01)
        if data.message_id in [MessageId.SEND_STANDARD, MessageId.SEND_EXTENDED]:
            dir_ack = _create_direct_ack(data)
            self._protocol.data_received(bytes(dir_ack))
            await asyncio.sleep(0.01)

    def start_reader(self):
        """Start the reader."""
        if not self._reader_lock.locked():
            self._closing = False
            self._start_reader()

    # pylint: disable=no-self-use
    async def async_test_connection(self):
        """Test the connection to the hub."""
        return True

    def write_eof(self):
        """Not implemented."""
        raise NotImplementedError("HTTP connections do not support end-of-file")

    def writelines(self, list_of_data):
        """Not implemented."""
        raise NotImplementedError("HTTP connections do not support writelines")

    # pylint: disable=broad-except
    async def _ensure_reader(self):
        _LOGGER.info("Insteon mock reader started")
        await self._webserver.async_start()
        async with self._reader_lock:
            while not self._closing:
                buffer = None
                async with self._read_write_lock:
                    buffer = await self._webserver.queue.get()
                    if buffer:
                        _LOGGER.debug("New buffer: %s", buffer)
                        buffer = self._check_strong_nak(buffer)
                        try:
                            bin_buffer = unhexlify(buffer)
                        except (Error, Incomplete):
                            _LOGGER.warning("Invalid buffer: %s", buffer)
                        else:
                            self._protocol.data_received(bin_buffer)
                if not self._closing:
                    await asyncio.sleep(READ_WAIT)
        _LOGGER.info("Insteon mock reader stopped")

    def _reader_closed_callback(self, exc):
        """Call when the reader closes."""
        self._closing = True
        self._protocol.connection_lost(exc)

    def _check_strong_nak(self, buffer):
        """Check if a NAK message is received with multiple `NAKs`.

        There appears to be a bug in the Hub that produces a series
        of NAK codes rather than returning the original message
        with a single NAK.
        """
        naks = buffer.count("15")
        if (naks >= 9 or naks == len(buffer) / 2) and self._last_msg is not None:
            return self._last_msg.hex() + "15"
        return buffer

    # pylint: disable=unused-argument
    def _start_reader(self, future=None):
        _LOGGER.debug("Starting the buffer reader")
        if not self._closing:
            self._reader_task = asyncio.ensure_future(self._ensure_reader())
            self._reader_task.add_done_callback(self._reader_closed_callback)

    async def _stop_reader(self, reconnect=False):
        _LOGGER.debug("Stopping the reader and reconnect is %s", reconnect)
        self.close()
        if self._reader_lock.locked():
            if not reconnect:
                self._reader_task.remove_done_callback(self._reader_closed_callback)
