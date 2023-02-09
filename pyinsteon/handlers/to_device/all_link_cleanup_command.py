"""Handle an outbound All-Link Broadcast message to a group."""

from abc import ABCMeta

from .. import (
    ack_handler,
    all_link_cleanup_ack_handler,
    all_link_cleanup_nak_handler,
    nak_handler,
)
from ...constants import MessageFlagType
from ..outbound_base import OutboundHandlerBase


class AllLinkCleanupCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound All-Link clean-up message handling."""

    __meta__ = ABCMeta

    def __init__(self, topic, address, group):
        """Init the DirectCommandHandlerBase class."""
        super().__init__(
            topic=topic,
            address=address,
            group=group,
            message_type=MessageFlagType.ALL_LINK_CLEANUP,
        )

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._address, **kwargs)

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
        await self._async_handle_ack(cmd1=cmd1, cmd2=cmd2, user_data=user_data)

    @nak_handler
    async def async_handle_nak(self, cmd1, cmd2, user_data):
        """Handle the message NAK."""
        await self._async_handle_nak()

    @all_link_cleanup_ack_handler
    def handle_all_link_ack(self, target, cmd1, cmd2, user_data, hops_left):
        """Handle the All-LInk Command ACK."""

    @all_link_cleanup_nak_handler
    def handle_all_link_nak(self, target, cmd1, cmd2, user_data, hops_left):
        """Handle the All-LInk Command NAK."""
