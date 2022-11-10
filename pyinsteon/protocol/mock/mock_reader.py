"""Mock reader used by the MockTransport class."""
import asyncio
import logging
from http.server import BaseHTTPRequestHandler

_LOGGER = logging.getLogger(__name__)
input_buffer = asyncio.Queue()


class MockReader(BaseHTTPRequestHandler):
    """Web server to accept inbound commands."""

    # pylint: disable=invalid-name
    def do_GET(self):
        """Respond to standard get requests."""
        self._set_response()
        self.wfile.write(
            bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8")
        )
        self.wfile.write(bytes(f"<p>Request: {self.path}</p>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

    def do_POST(self):
        """Handle a post request."""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        _LOGGER.info(
            "POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            str(self.path),
            str(self.headers),
            post_data.decode("utf-8"),
        )

        self._set_response()
        self.wfile.write(f"POST request for {self.path}".encode("utf-8"))
        input_buffer.put_nowait(post_data.decode("utf-8"))

    def _set_response(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
