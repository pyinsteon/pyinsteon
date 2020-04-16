"""Handle an outbound All-Link Broadcast message to a group."""

import asyncio
from abc import ABCMeta

from .. import ack_handler, all_link_cleanup_ack_handler, all_link_cleanup_nak_handler
from ...address import Address
from ...constants import MessageFlagType
from ..outbound_base import OutboundHandlerBase


class AllLinkCleanupCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound All-Link clean-up message handling."""

    __meta__ = ABCMeta

    def __init__(self, topic, address, group):
        """Init the DirectCommandHandlerBase class."""
        self._address = Address(address)
        self._group = group
        self._response_lock = asyncio.Lock()
        super().__init__(
            topic=topic,
            address=self._address,
            group=self._group,
            message_type=MessageFlagType.ALL_LINK_CLEANUP,
        )

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._address, **kwargs)

    # pylint: disable=arguments-differ
    @ack_handler(wait_response=False)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
        pass

    @all_link_cleanup_ack_handler
    def handle_all_link_ack(self, target, cmd1, cmd2, user_data, hops_left):
        """Handle the All-LInk Command ACK."""
        pass

    @all_link_cleanup_nak_handler
    def handle_all_link_nak(self, target, cmd1, cmd2, user_data, hops_left):
        """Handle the All-LInk Command NAK."""
        pass
