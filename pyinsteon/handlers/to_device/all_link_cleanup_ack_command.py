"""Send an All-Link Cleanup ACK message to a device."""

import asyncio

from .. import ack_handler
from ...address import Address
from ...constants import MessageFlagType
from ..outbound_base import OutboundHandlerBase


class AllLinkCleanupAckCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound All-Link Cleanup ACK message handling."""

    def __init__(self, topic, address, group):
        """Init the DirectCommandHandlerBase class."""
        self._address = Address(address)
        self._group = group
        self._response_lock = asyncio.Lock()
        super().__init__(
            topic=topic,
            address=self._address,
            group=self._group,
            message_type=MessageFlagType.ALL_LINK_CLEANUP_ACK,
        )

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._address, **kwargs)

    # pylint: disable=arguments-differ
    @ack_handler(wait_response=False)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
