"""Mock reader used by the MockTransport class."""
import asyncio

from aiohttp import web

input_buffer = asyncio.Queue()


def _set_response(web_response: web.Response):
    web_response.headers.add("Content-type", "text/html")
    web_response.set_status(200)
    return web_response


class MockReader:
    """Web server to accept inbound commands."""

    def __init__(self, host="127.0.0.1", port=8080):
        """Init the MockReader class."""
        self._host = host
        self._port = port
        self._app = web.Application()
        self._app.router.add_get("/", self.do_get)
        self._app.router.add_post("/input", self.do_post)
        self._site = None
        self._queue = asyncio.Queue()

    @property
    def queue(self):
        """Return the data queue."""
        return self._queue

    async def async_start(self):
        """Start the web server."""
        runner = web.AppRunner(self._app)
        await runner.setup()
        self._site = web.TCPSite(runner=runner, host=self._host, port=self._port)
        await self._site.start()

    def stop(self):
        """Stop the listener."""
        self._site.stop()

    # pylint: disable=no-self-use
    def do_get(self, request):
        """Respond to standard get requests."""
        response = "<html><head><title>https://pythonbasics.org</title></head>"
        response = f"{response}<body>"
        response = f"{response}<p>Web server is up and listening.  POST messages to `/input`.</p>"
        response = f"{response}</body></html>"
        web_response = web.Response(text=response)
        web_response = _set_response(web_response)
        return web_response

    async def do_post(self, request: web.Request):
        """Handle a post request."""
        json_data = await request.json()
        for _, value in json_data.items():
            await self._queue.put(value)
            await asyncio.sleep(0.5)
        return web.Response(text=str(json_data))
