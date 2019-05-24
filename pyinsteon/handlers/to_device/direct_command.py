"""Handle an outbound direct message to a device."""

from abc import ABCMeta
import asyncio
from ..outbound_base import OutboundHandlerBase
from ...address import Address
from .. import ack_handler, direct_nak_handler, direct_ack_handler

TIMEOUT = 3  # Wait time for device response

class DirectCommandHandlerBase(OutboundHandlerBase):
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
        result = await super().async_send(address=self._address, **kwargs)
        return result

    @ack_handler(wait_response=True)
    def handle_ack(self, cmd2, user_data):
        """Handle the message ACK."""

    @direct_nak_handler
    def handle_direct_nak(self, cmd2, target, user_data):
        """Handle the message ACK."""

    @direct_ack_handler
    def handle_direct_ack(self, cmd2, target, user_data):
        """Handle the direct ACK."""
