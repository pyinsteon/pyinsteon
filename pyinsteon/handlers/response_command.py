"""Handle an outbound message that expects a response."""

from abc import ABCMeta, abstractmethod
import asyncio
from .outbound_base import OutboundHandlerBase
from ..address import Address
from . import ack_handler, response_handler

TIMEOUT = 3  # Wait time for device response

class ResponseCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound direct message handling."""

    __meta__ = ABCMeta

    def __init__(self, address, command):
        """Init the DirectCommandHandlerBase class."""
        self._address = Address(address)
        self._response_lock = asyncio.Lock()
        super().__init__('{}.{}'.format(self._address.id, command))
        # We override the _send_topic to ensrue the address does not go as
        # part of the topic. Address is a key word argument for Direct Commands
        self._send_topic = command

    @property
    def response_lock(self) -> asyncio.Lock:
        """Lock to manage the response between ACK and Direct ACK."""
        return self._response_lock

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        if self.response_lock.locked():
            self.response_lock.release()
        # await self.response_lock.acquire()
        response = await super().async_send(address=self._address, **kwargs)
        if self.response_lock.locked():
            self.response_lock.release()
        return response

    @abstractmethod
    @ack_handler(wait_response=True)
    def handle_ack(self, **kwargs):
        """Handle the message ACK."""

    @abstractmethod
    @response_handler()
    def handle_response(self, cmd2, target, user_data):
        """Handle the message response."""
