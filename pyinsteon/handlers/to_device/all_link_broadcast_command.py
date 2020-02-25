"""Handle an outbound All-Link Broadcast message to a group."""

import asyncio
from abc import ABCMeta

from .. import ack_handler
from ...address import Address
from ...constants import MessageFlagType
from ..outbound_base import OutboundHandlerBase


class AllLinkBroadcastCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound All-Link broadcast message handling."""

    __meta__ = ABCMeta

    def __init__(self, topic, group):
        """Init the DirectCommandHandlerBase class."""
        self._address = Address(bytearray([0x00, 0x00, group]))
        self._response_lock = asyncio.Lock()
        super().__init__(
            topic=topic,
            address=self._address,
            group=None,
            message_type=MessageFlagType.ALL_LINK_BROADCAST,
        )

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._address, **kwargs)

    # pylint: disable=arguments-differ
    @ack_handler(wait_response=False)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
