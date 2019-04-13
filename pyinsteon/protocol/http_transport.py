"""HTTP Transport  for asyncio."""
import asyncio
from binascii import unhexlify
from contextlib import suppress
import logging

import aiohttp


_LOGGER = logging.getLogger(__name__)


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

    def __init__(self, protocol, host, username, password, port=25105, loop=None):
        """Init the HttpTransport class."""
        super().__init__()
        self._loop = loop if loop else asyncio.get_event_loop()
        self._protocol = protocol
        self._host = host
        self._port = port
        auth = aiohttp.BasicAuth(username, password)
        self._auth = auth

        self._closing = False
        self._protocol_paused = False
        self._max_read_size = 1024
        self._write_buffer = []
        self._has_reader = False
        self._has_writer = False
        self._read_write_lock = asyncio.Lock(loop=self._loop)
        self._last_read = asyncio.Queue(loop=self._loop)
        self._restart_reader = True
        self._reader_task = None

        self._start_reader()

    def abort(self):
        """Alternative to closing the transport."""
        self.close()

    def can_write_eof(self):
        """Always return False."""
        return False

    def is_closing(self):
        """True if the transport is closed or in the process of closing."""
        return self._closing

    def close(self):
        """Close the transport."""
        _LOGGER.debug("Closing Hub session")
        self._closing = True
        self._restart_reader = False

    def get_write_buffer_size(self):
        """Always return 0 (i.e. none)."""
        return 0

    def pause_reading(self):
        """Pause the read."""
        asyncio.ensure_future(self._stop_reader(False), loop=self._loop)

    def resume_reading(self):
        """Resume the reader."""
        self._restart_reader = True
        self._start_reader()

    def set_write_buffer_limits(self, high=None, low=None):
        """Not implemented."""
        raise NotImplementedError(
            "HTTP connections do not support write buffer limits")

    def write(self, data):
        """Write data to the transport."""
        from .msg_to_url import convert_to_url
        _LOGGER.debug("..................Writing a message..............")
        url = convert_to_url(self._host, self._port, data)
        asyncio.ensure_future(self._async_write(url), loop=self._loop)

    async def async_test_connection(self):
        """Test the connection to the hub."""
        url = 'http://{:s}:{:d}/buffstatus.xml'.format(self._host, self._port)
        response_status = 999
        try:
            async with aiohttp.ClientSession(loop=self._loop,
                                             auth=self._auth) as session:
                async with session.get(url, timeout=10) as response:
                    if response:
                        response_status = response.status
                        if response.status == 200:
                            _LOGGER.debug('Test connection status is %d',
                                          response.status)
                            return True
                        self._log_error(response.status)
                        _LOGGER.debug('Connection test failed')
                        return False

        # pylint: disable=broad-except
        except Exception as e:
            _LOGGER.error('An aiohttp error occurred: %s with status %s',
                          str(e), response_status)
        _LOGGER.debug('Connection test failed')
        self.close()
        return False

    async def _async_write(self, url):
        """Write data to the transport asyncronously."""
        return_status = 500
        _LOGGER.debug("Writing message: %s", url)
        try:
            await self._read_write_lock
            async with aiohttp.ClientSession(loop=self._loop,
                                             auth=self._auth) as session:
                async with session.post(url, timeout=10) as response:
                    return_status = response.status
                    _LOGGER.debug("Post status: %s", response.status)
                    if response.status == 200:
                        self._write_last_read(0)
                    else:
                        self._log_error(response.status)
                        await self._stop_reader(False)
        except aiohttp.ClientError:
            _LOGGER.error('Reconnect to Hub (ClienError)')
            await self._stop_reader(True)
        except asyncio.TimeoutError:
            _LOGGER.error('Reconnect to Hub (TimeoutError)')
            await self._stop_reader(True)

        if self._read_write_lock.locked():
            self._read_write_lock.release()
        return return_status

    def write_eof(self):
        """Not implemented."""
        raise NotImplementedError(
            "HTTP connections do not support end-of-file")

    def writelines(self, list_of_data):
        """Not implemented."""
        raise NotImplementedError(
            "HTTP connections do not support writelines")

    def clear_buffer(self):
        """Clear the Hub read buffer."""
        asyncio.wait(self._clear_buffer())

    async def _clear_buffer(self):
        _LOGGER.debug("..................Clearing the buffer..............")
        url = 'http://{:s}:{:d}/1?XB=M=1'.format(self._host, self._port)
        await self._async_write(url)

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    # pylint: disable=broad-except
    async def _ensure_reader(self):
        _LOGGER.info('Insteon Hub reader started')
        await self._clear_buffer()
        self._write_last_read(0)
        url = 'http://{:s}:{:d}/buffstatus.xml'.format(self._host, self._port)
        _LOGGER.debug('Calling connection made')
        _LOGGER.debug('Protocol: %s', self._protocol)
        self._protocol.connection_made(self)
        while self._restart_reader and not self._closing:
            try:
                await self._read_write_lock
                async with aiohttp.ClientSession(loop=self._loop,
                                                 auth=self._auth) as session:
                    async with session.get(url, timeout=10) as response:
                        buffer = None
                        # _LOGGER.debug("Reader status: %d", response.status)
                        if response.status == 200:
                            html = await response.text()
                            buffer = await self._parse_buffer(html)
                        else:
                            self._log_error(response.status)
                            await self._stop_reader(False)
                if self._read_write_lock.locked():
                    self._read_write_lock.release()
                if buffer:
                    _LOGGER.debug('New buffer: %s', buffer)
                    bin_buffer = unhexlify(buffer)
                    self._protocol.data_received(bin_buffer)
                await asyncio.sleep(1, loop=self._loop)

            except asyncio.CancelledError:
                _LOGGER.debug('Stop connection to Hub (loop stopped)')
                await self._stop_reader(False)
            except GeneratorExit:
                _LOGGER.debug('Stop connection to Hub (GeneratorExit)')
                await self._stop_reader(False)
            except aiohttp.ClientError:
                _LOGGER.debug('Reconnect to Hub (ClientError)')
                await self._stop_reader(True)
            except asyncio.TimeoutError:
                _LOGGER.error('Reconnect to Hub (TimeoutError)')
                await self._stop_reader(True)
            except Exception as e:
                _LOGGER.debug('Stop reading due to %s', str(e))
                await self._stop_reader(False)
        _LOGGER.info('Insteon Hub reader stopped')
        return

    async def _parse_buffer(self, html):
        last_stop = 0
        if not self._last_read.empty():
            last_stop = self._last_read.get_nowait()
        buffer = ''
        raw_text = html.replace('<response><BS>', '')
        raw_text = raw_text.replace('</BS></response>', '')
        raw_text = raw_text.strip()
        if raw_text[:199] == '0' * 200:
            # Likely the buffer was cleared
            return None
        this_stop = int(raw_text[-2:], 16)
        if this_stop > last_stop:
            _LOGGER.debug('Buffer from %d to %d', last_stop, this_stop)
            buffer = raw_text[last_stop:this_stop]
        elif this_stop < last_stop:
            _LOGGER.debug('Buffer from %d to 200 and 0 to %d',
                          last_stop, this_stop)
            buffer_hi = raw_text[last_stop:200]
            if buffer_hi == '0' * len(buffer_hi):
                # The buffer was probably reset since the last read
                buffer_hi = ''
            buffer_low = raw_text[0:this_stop]
            buffer = '{:s}{:s}'.format(buffer_hi, buffer_low)
        else:
            buffer = None
        self._write_last_read(this_stop)
        return buffer

    def _write_last_read(self, val):
        while not self._last_read.empty():
            self._last_read.get_nowait()
        self._last_read.put_nowait(val)

    # pylint: disable=unused-argument
    def _start_reader(self, future=None):
        if self._restart_reader:
            _LOGGER.debug("Starting the buffer reader")
            self._reader_task = asyncio.ensure_future(self._ensure_reader(),
                                                      loop=self._loop)
            self._reader_task.add_done_callback(self._start_reader)

    async def _stop_reader(self, reconnect=False):
        _LOGGER.debug('Stopping the reader and reconnect is %s', reconnect)
        self._restart_reader = False
        if self._reader_task:
            self._reader_task.remove_done_callback(self._start_reader)
            self._reader_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._reader_task
                await asyncio.sleep(0, loop=self._loop)
        await self._protocol.pause_writing()
        if reconnect:
            _LOGGER.debug("We want to reconnect so we do...")
            self._protocol.connection_lost(True)

    def _log_error(self, status):
        if status == 401:
            _LOGGER.error('Athentication error, check your configuration')
            _LOGGER.error('If configuration is correct and restart the Hub')
            _LOGGER.error('System must be restared to reconnect to hub')
        elif status == 404:
            _LOGGER.error('Hub not found at http://%s:%d, check configuration',
                          self._host, self._port)
        elif status in range(500, 600):
            _LOGGER.error('Hub returned a server error')
            _LOGGER.error('Restart the Hub and try again')
        else:
            _LOGGER.error('An unknown error has occured')
            _LOGGER.error('Check the configuration and restart the Hub and '
                          'the application')
