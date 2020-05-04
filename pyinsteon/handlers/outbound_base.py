"""Mock message handling via Chain of Command pattern."""
import asyncio
from abc import ABCMeta

from . import ResponseStatus
from ..utils import publish_topic
from ..utils import build_topic
from .inbound_base import InboundHandlerBase


MSG_TIME = 4  # seconds to send each message in queue, used for timeout below


def _calc_timeout():
    """Calculate the time to wait for a message to be sent."""
    from .. import devices

    if devices and devices.modem:
        return devices.modem.protocol.message_queue.qsize() * MSG_TIME + MSG_TIME
    return MSG_TIME


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
        publish_topic(send_topic, **kwargs)
        timeout = _calc_timeout()
        try:
            return await asyncio.wait_for(self._message_response.get(), timeout)
        except asyncio.TimeoutError:
            pass
        return ResponseStatus.UNSENT
