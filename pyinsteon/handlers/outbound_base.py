"""Mock message handling via Chain of Command pattern."""
import asyncio
from abc import ABCMeta

import async_timeout

from ..constants import ResponseStatus
from ..utils import build_topic, publish_topic
from . import ack_handler
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
        self._send_topic = build_topic(
            topic=self._topic,
            prefix="send",
            address=None,
            group=None,
            message_type=self._message_type,
        )

    @property
    def message_response(self) -> asyncio.Queue:
        """Message response queue to manage message status."""
        return self._message_response

    def send(self, **kwargs):
        """Sent the message."""
        asyncio.ensure_future(self.async_send(**kwargs))

    async def async_send(self, **kwargs):
        """Send the message and wait for a status."""

        # Empty the message queue
        while not self._message_response.empty():
            try:
                self._message_response.get_nowait()
            except asyncio.QueueEmpty:
                pass

        publish_topic(self._send_topic, **kwargs)

        try:
            async with async_timeout.timeout(_calc_timeout()):
                return await self._message_response.get()
        except asyncio.TimeoutError:
            return ResponseStatus.FAILURE

    @ack_handler
    def handle_ack(self, **kwargs):
        """Handle the ACK processing."""
        user_data = kwargs.get("user_data")
        if self._group is not None and user_data is not None:
            curr_group = user_data.get("d1", 1)
            if self._group != curr_group:
                return
        self._message_response.put_nowait(ResponseStatus.SUCCESS)
