"""Handle an outbound direct message to a device."""

import asyncio
from abc import ABCMeta

from .. import ack_handler, direct_ack_handler, direct_nak_handler
from ...address import Address
from ...constants import MessageFlagType
from ..outbound_base import OutboundHandlerBase

TIMEOUT = 3  # Wait time for device response


class DirectCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound direct message handling."""

    __meta__ = ABCMeta

    def __init__(self, topic, address, group=None):
        """Init the DirectCommandHandlerBase class."""
        self._address = Address(address)
        self._group = group
        self._response_lock = asyncio.Lock()
        super().__init__(
            topic, address=address, group=group, message_type=MessageFlagType.DIRECT
        )

    @property
    def response_lock(self) -> asyncio.Lock:
        """Lock to manage the response between ACK and Direct ACK."""
        return self._response_lock

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._address, **kwargs)

    # pylint: disable=arguments-differ
    @ack_handler(wait_response=True)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""

    @direct_nak_handler
    def handle_direct_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the message ACK."""
        pass

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK."""
