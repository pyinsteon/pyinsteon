"""Mock message handling via Chain of Command pattern."""
import asyncio
from abc import ABCMeta
from .. import pub
from .inbound_base import InboundHandlerBase
from . import ResponseStatus


TIMEOUT = 60 * 3  # It should not take more than 3 minutes for a message send (I hope)

class OutboundHandlerBase(InboundHandlerBase):
    """Manage a message chain."""

    __meta__ = ABCMeta

    def __init__(self, topic):
        """Init the MessageManager."""
        self._message_response = asyncio.Queue()
        self._send_topic = topic
        super().__init__(topic)

    @property
    def message_response(self) -> asyncio.Queue:
        """Message response queue to manage message status."""
        return self._message_response

    def send(self, **kwargs):
        """Sent the message."""
        asyncio.ensure_future(self.async_send(**kwargs))

    async def async_send(self, **kwargs):
        """Send the message and wait for a status."""
        while not self._message_response.empty():
            # Empty the message queue
            try:
                self._message_response.get_nowait()
            except asyncio.QueueEmpty:
                pass
        pub.sendMessage('send.{}'.format(self._send_topic), **kwargs)
        try:
            test = await asyncio.wait_for(
                self._message_response.get(), TIMEOUT)
            return test
        except asyncio.TimeoutError:
            return ResponseStatus.UNSENT
