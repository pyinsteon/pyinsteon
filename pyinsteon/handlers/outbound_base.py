"""Mock message handling via Chain of Command pattern."""
import asyncio
from abc import ABC, abstractmethod, abstractproperty
from typing import Callable
from .utils import topic_to_message, response_handler
from .. import pub

TIMEOUT = 3

class OutboundBase(ABC):
    """Manage a message chain."""

    def __init__(self, msg_type: int, cmd1: int = None, cmd2: int = None):
        """Init the MessageManager."""
        self._msg_response_queue = asyncio.Queue()
        self._response_lock = asyncio.Lock()
        self._subscribe_topics()
        self._subscribers = []
        self._topic, self._message_factory = some_method(msg_type, cmd1, cmd2, extended)

    def send(self, *args, **kwargs):
        """Sent the message."""
        asyncio.ensure_future(self.async_send(*args, **kwargs))

    async def async_send(self, *args, **kwargs):
        """Send the message."""
        topic, msg = self._message_factory(*args, **kwargs)
        pub.sendMessage(topic, msg=msg)
        return await self._msg_response_queue.get()

    @abstractmethod
    @response_handler
    def handle_response(self, **kwargs):
        """Handle inbound message."""

    def subscribe(self, callback: Callable):
        """Subscribe to this message handler."""
        self._subscribers.append(callback)

    def _wait_ack(self, **kwargs):
        """Wait for message ACK from IM."""
        asyncio.ensure_future(self._async_wait_ack())

    async def _async_wait_ack(self):
        try:
            if not self._response_lock.locked():
                await asyncio.wait_for(
                    self._response_lock.acquire(), TIMEOUT
                )
        except asyncio.TimeoutError:
            self._msg_response_queue.put_nowait('Timeout')

    def _handle_direct_nak(self, **kwargs):
        """Handle the direct NAK by sending a 'maybe' response."""
        self._msg_response_queue.put_nowait('maybe')

    def _subscribe_topics(self):
        """Subscribe to the message ACK and Direct ACK messages."""
        ack_topic = 'ack.{}'.format(self._topic)
        if self._topic[-6] == 'direct':
            direct_ack_topic = '{}._ack'.format(self._topic)
            direct_nak_topic = '{}._nak'.format(self._topic)
        else:
            direct_ack_topic = '{}.direct_ack'.format(self._topic)
            direct_nak_topic = '{}.direct_nak'.format(self._topic)
        pub.subscribe(self._wait_ack, ack_topic)
        pub.subscribe(self.handle_response, direct_ack_topic)
        pub.subscribe(self._handle_direct_nak, direct_nak_topic)
