"""Read and write to the Hub."""
import asyncio
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)


def _log_error(status):
    if status == 401:
        _LOGGER.error("Athentication error, check your configuration")
        _LOGGER.error("If configuration is correct and restart the Hub")
        _LOGGER.error("System must be restared to reconnect to hub")
    elif status == 404:
        _LOGGER.error("Hub not found, check configuration")
    elif status in range(500, 600):
        _LOGGER.error("Hub returned a server error")
        _LOGGER.error("Restart the Hub and try again")
    else:
        _LOGGER.error("An unknown error has occured")
        _LOGGER.error(
            "Check the configuration and restart the Hub and " "the application"
        )


class HttpReaderWriter:
    """HTTP reader and writer."""

    def __init__(self, auth):
        """Init the HttpReaderWriter class."""
        self._auth = auth
        self._last_read = asyncio.Queue()

    async def async_test_connection(self, url):
        """Test the connection to the hub."""
        response_status = 999
        try:
            async with aiohttp.ClientSession(auth=self._auth) as session:
                async with session.get(url, timeout=10) as response:
                    if response:
                        response_status = response.status
                        if response.status == 200:
                            _LOGGER.debug(
                                "Test connection status is %d", response.status
                            )
                            return True
                        _log_error(response.status)
                        _LOGGER.debug("Connection test failed")
                        return False

        # pylint: disable=broad-except
        except Exception as ex:
            _LOGGER.error(
                "An aiohttp error occurred: %s with status %s", str(ex), response_status
            )
        _LOGGER.debug("Connection test failed")
        return False

    async def async_read(self, session, url):
        """Read from the url."""
        from .http_transport import HubConnectionException

        try:
            async with session.get(url) as response:
                # _LOGGER.debug("Reader status: %d", response.status)
                if response.status == 200:
                    html = await response.text()
                else:
                    _log_error(response.status)
                    raise HubConnectionException(
                        "Connection status error: {}".format(response.status)
                    )
        except (asyncio.TimeoutError, aiohttp.ClientError) as ex:
            await session.close()
            _LOGGER.error("Session error: %s", str(ex))
            raise HubConnectionException(str(ex))
        return await self._parse_buffer(html)

    async def async_write(self, url):
        """Write data to the transport asyncronously."""
        return_status = 500
        _LOGGER.debug("Writing message: %s", url)
        try:
            async with aiohttp.ClientSession(auth=self._auth) as session:
                async with session.post(url, timeout=10) as response:
                    return_status = response.status
                    _LOGGER.debug("Post status: %s", response.status)
                    if response.status == 200:
                        await self.reset_reader()
                    else:
                        _log_error(response.status)
        except aiohttp.ClientError:
            _LOGGER.error("Hub write failure (ClienError)")
        except asyncio.TimeoutError:
            _LOGGER.error("Hub write failure (TimeoutError)")

        return return_status

    async def reset_reader(self):
        """Reset the reader to default position."""
        await self._set_last_read(0)

    async def _parse_buffer(self, html):
        last_stop = 0
        if not self._last_read.empty():
            last_stop = self._last_read.get_nowait()
        buffer = ""
        raw_text = html.replace("<response><BS>", "")
        raw_text = raw_text.replace("</BS></response>", "")
        raw_text = raw_text.strip()
        if raw_text[:199] == "0" * 200:
            # Likely the buffer was cleared
            return None
        this_stop = int(raw_text[-2:], 16)
        if this_stop > last_stop:
            _LOGGER.debug("Raw buffer: %s", raw_text)
            _LOGGER.debug("Buffer from %d to %d", last_stop, this_stop)
            buffer = raw_text[last_stop:this_stop]
        elif this_stop < last_stop:
            _LOGGER.debug("Raw buffer: %s", raw_text)
            _LOGGER.debug("Buffer from %d to 200 and 0 to %d", last_stop, this_stop)
            buffer_hi = raw_text[last_stop:200]
            if buffer_hi == "0" * len(buffer_hi):
                # The buffer was probably reset since the last read
                buffer_hi = ""
            buffer_low = raw_text[0:this_stop]
            buffer = "{:s}{:s}".format(buffer_hi, buffer_low)
        else:
            buffer = None
        await self._set_last_read(this_stop)
        return buffer

    async def _set_last_read(self, val):
        while not self._last_read.empty():
            await self._last_read.get()
        await self._last_read.put(val)
