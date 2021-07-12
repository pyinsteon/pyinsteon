"""HTTP Transport  for asyncio."""
import asyncio
import logging
from binascii import unhexlify
from contextlib import suppress

import aiohttp

from .http_reader_writer import HttpReaderWriter
from .hub_connection_exception import HubConnectionException
from .msg_to_url import convert_to_url

_LOGGER = logging.getLogger(__name__)
READ_WAIT = 0.5
SESSION_RETRIES = 30
RECONNECT_WAIT = 7


async def async_connect_http(host, username, password, protocol, port=None):
    """Connect to the Hub Version 2 via HTTP."""
    port = 25105 if not port else port
    transport = HttpTransport(
        protocol=protocol, host=host, port=port, username=username, password=password
    )
    if await transport.async_test_connection():
        transport.start_reader()
        protocol.connection_made(transport)
        return transport
    return None


# This transport is designed for the Hub version 2.
# Hub version 1 should use socket interface on port 9761.
# pylint: disable=too-many-instance-attributes
class HttpTransport(asyncio.Transport):
    """An asyncio transport model of an HTTP communication channel.

    A transport class is an abstraction of a communication channel.
    This allows protocol implementations to be developed against the
    transport abstraction without needing to know the details of the
    underlying channel, such as whether it is a pipe, a socket, or
    indeed an HTTP connection.


    You generally won’t instantiate a transport yourself; instead, you
    will call `create_http_connection` which will create the
    transport and try to initiate the underlying communication channel,
    calling you back when it succeeds.
    """

    def __init__(self, protocol, host, username, password, port=25105):
        """Init the HttpTransport class."""
        super().__init__()
        self._protocol = protocol
        self._host = host
        self._port = port
        self._auth = aiohttp.BasicAuth(username, password)
        self._reader_writer = HttpReaderWriter(self._auth)

        self._closing = False
        self._read_write_lock = asyncio.Lock()
        self._last_read = asyncio.Queue()
        self._last_msg = None
        self._reader_task = None

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

    def get_write_buffer_size(self):
        """Rreturn 0 (i.e. none) always."""
        return 0

    def pause_reading(self):
        """Pause the read."""
        asyncio.ensure_future(self._stop_reader(False))

    def resume_reading(self):
        """Resume the reader."""
        self._start_reader()

    def set_write_buffer_limits(self, high=None, low=None):
        """Not implemented."""
        raise NotImplementedError("HTTP connections do not support write buffer limits")

    def write(self, data):
        """Write data to the transport."""
        asyncio.ensure_future(self.async_write(data))

    async def async_write(self, data):
        """Async write to the transport."""
        url = convert_to_url(self._host, self._port, data)
        await self._async_write_url(url=url, msg=bytes(data))

    def start_reader(self):
        """Start the reader."""
        if self._reader_task is None:
            self._start_reader()

    async def _async_write_url(self, url, msg=None):
        """Write the message to the Hub."""
        async with self._read_write_lock:
            response_status = 0
            retry = 0
            while response_status != 200 and retry < 5:
                if self.is_closing():
                    if self._read_write_lock.locked():
                        self._read_write_lock.release()
                    return
                response_status = await self._reader_writer.async_write(url)
                if response_status != 200:
                    _LOGGER.debug("Hub write request failed for url %s", url)
                    retry += 1
                    await asyncio.sleep(READ_WAIT)
                else:
                    self._last_msg = msg

    async def async_test_connection(self):
        """Test the connection to the hub."""
        url = "http://{:s}:{:d}/buffstatus.xml".format(self._host, self._port)
        response = await self._reader_writer.async_test_connection(url)
        if not response:
            self.close()
        return response

    def write_eof(self):
        """Not implemented."""
        raise NotImplementedError("HTTP connections do not support end-of-file")

    def writelines(self, list_of_data):
        """Not implemented."""
        raise NotImplementedError("HTTP connections do not support writelines")

    async def _clear_buffer(self):
        _LOGGER.debug("..................Clearing the buffer..............")
        url = "http://{:s}:{:d}/1?XB=M=1".format(self._host, self._port)
        await self._async_write_url(url)

    # pylint: disable=broad-except
    async def _ensure_reader(self):
        _LOGGER.info("Insteon Hub reader started")
        await self._clear_buffer()
        await self._reader_writer.reset_reader()
        url = "http://{:s}:{:d}/buffstatus.xml".format(self._host, self._port)
        retry = 0
        while not self._closing:
            buffer = None
            async with self._read_write_lock:
                try:
                    buffer = await self._reader_writer.async_read(url)
                except HubConnectionException:
                    retry += 1
                    _LOGGER.debug("Connection retry: %d", retry)
                    await asyncio.sleep(RECONNECT_WAIT)
                    if retry >= SESSION_RETRIES:
                        _LOGGER.error(
                            "Closing connection Hub after %d retries", SESSION_RETRIES
                        )
                        self.close()

                except (asyncio.CancelledError, GeneratorExit) as ex:
                    _LOGGER.debug("Stop connection to Hub: %s", ex)
                    self.close()

                else:
                    retry = 0
                    if buffer:
                        _LOGGER.debug("New buffer: %s", buffer)
                        buffer = self._check_strong_nak(buffer)
                        bin_buffer = unhexlify(buffer)
                        self._protocol.data_received(bin_buffer)
            if not self.is_closing():
                await asyncio.sleep(READ_WAIT)
        _LOGGER.info("Insteon Hub reader stopped")

    def _check_strong_nak(self, buffer):
        """Check if a NAK message is received with multiple NAKs.

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
            self._reader_task.add_done_callback(self._protocol.connection_lost)

    async def _stop_reader(self, reconnect=False):
        _LOGGER.debug("Stopping the reader and reconnect is %s", reconnect)
        self.close()
        if self._reader_task:
            if not reconnect:
                self._reader_task.remove_done_callback(self._protocol.connection_lost)
            self._reader_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reader_task
                await asyncio.sleep(0)
