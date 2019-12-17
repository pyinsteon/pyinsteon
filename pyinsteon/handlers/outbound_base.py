"""Mock message handling via Chain of Command pattern."""
import asyncio
from abc import ABCMeta
from .. import pub
from .inbound_base import InboundHandlerBase
from . import ResponseStatus
from ..utils import build_topic


# It should not take more than 3 minutes for a message send (I hope)
TIMEOUT = 60 * 3


class OutboundHandlerBase(InboundHandlerBase):
    """Manage a message chain."""

    __meta__ = ABCMeta

    def __init__(self, topic, address=None, group=None, message_type=None):
        """Init the MessageManager."""
        self._message_response = asyncio.Queue()
        self._message_type = message_type
        super().__init__(topic, address=address, group=group, message_type=message_type)

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
        send_topic = build_topic(
            topic=self._topic,
            prefix="send",
            address=None,
            group=None,
            message_type=self._message_type,
        )
        pub.sendMessage(send_topic, **kwargs)
        try:
            test = await asyncio.wait_for(self._message_response.get(), TIMEOUT)
            return test
        except asyncio.TimeoutError:
            return ResponseStatus.UNSENT
