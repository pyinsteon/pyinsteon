"""Mock message handling via Chain of Command pattern."""
from abc import ABCMeta
import asyncio
import logging

import async_timeout

from ..constants import ResponseStatus
from ..utils import build_topic, publish_topic
from .inbound_base import InboundHandlerBase

MSG_TIME = 180  # seconds to send each message in queue, used for timeout below
NAK_RETRIES = 9
NAK_RESEND_WAIT = 0.2
_LOGGER = logging.getLogger(__name__)


class OutboundHandlerBase(InboundHandlerBase):
    """Manage a message chain."""

    __meta__ = ABCMeta

    def __init__(self, topic, address=None, group=None, message_type=None):
        """Init the MessageManager."""
        self._message_response = asyncio.Queue()
        self._send_lock = asyncio.Lock()
        self._message_type = message_type
        super().__init__(topic, address=address, group=group, message_type=message_type)
        self._send_topic = build_topic(
            topic=self._topic,
            prefix="send",
            address=None,
            group=None,
            message_type=self._message_type,
        )
        self._nak_retries = NAK_RETRIES
        self._kwargs = {}

    @property
    def message_response(self) -> asyncio.Queue:
        """Message response queue to manage message status."""
        return self._message_response

    async def async_send(self, **kwargs):
        """Send the message and wait for a status."""
        async with self._send_lock:
            # Empty the message queue
            while not self._message_response.empty():
                try:
                    self._message_response.get_nowait()
                except asyncio.QueueEmpty:
                    pass

            self._nak_retries = NAK_RETRIES
            self._kwargs = kwargs
            publish_topic(self._send_topic, **self._kwargs)

            try:
                async with async_timeout.timeout(MSG_TIME):
                    return await self._message_response.get()
            except asyncio.TimeoutError:
                # Send a FAILURE message if this is running more than 180 seconds
                return ResponseStatus.FAILURE

    async def _async_handle_ack(self, **kwargs):
        """Handle the ACK processing."""
        await self._message_response.put(ResponseStatus.SUCCESS)

    async def _async_handle_nak(self, **kwargs):
        """Call from a command handler to handle the NAK response from the modem."""
        if not self._send_lock.locked():
            return
        if self._nak_retries:
            sleep_duration = (
                NAK_RESEND_WAIT * (NAK_RETRIES - self._nak_retries) + NAK_RESEND_WAIT
            )
            await asyncio.sleep(sleep_duration)
            publish_topic(self._send_topic, **self._kwargs)
            self._nak_retries -= 1
            return
        await self._message_response.put(ResponseStatus.FAILURE)
