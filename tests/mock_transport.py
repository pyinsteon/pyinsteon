"""Mock transport for testing."""
import asyncio

from pyinsteon.subscriber_base import SubscriberBase


class MockTransport(SubscriberBase, asyncio.Transport):
    """Mock transport for testing."""

    def __init__(
        self,
        protocol,
        read_queue: asyncio.Queue,
        write_queue: asyncio.Queue,
        random_nak=True,
    ):
        """Init the MockTransport class."""
        super().__init__(subscriber_topic="mock_transport")
        self._protocol = protocol
        self._read_queue = read_queue
        self._write_queue = write_queue
        self._random_nak = random_nak
        self._closing = False
        asyncio.ensure_future(self._process_read_queue())

    async def _process_read_queue(self):
        """Read the data queue."""
        while True:
            data = await self._read_queue.get()
            if data is None:
                break
            self._protocol.data_received(data)

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
        self._read_queue.put_nowait(None)
        self._closing = True

    def get_write_buffer_size(self):
        """Always return 0 (i.e. none)."""
        return 0

    def pause_reading(self):
        """Pause the read."""

    def resume_reading(self):
        """Resume the reader."""

    def set_write_buffer_limits(self, high=None, low=None):
        """Not implemented."""
        raise NotImplementedError("HTTP connections do not support write buffer limits")

    def write(self, data):
        """Write data to the transport."""
        from random import randint

        if isinstance(data, bytes):
            test_id = data[1]
        else:
            test_id = data.message_id
        self._write_queue.put_nowait(data)
        if test_id in [0x69, 0x6A]:
            return
        rand_num = randint(0, 100)
        ack_nak = 0x15 if rand_num < 10 and self._random_nak else 0x06
        ack = bytes(data) + bytes([ack_nak])
        self._protocol.data_received(ack)

    async def async_write(self, data):
        """Write to the transport."""
        self.write(data)
