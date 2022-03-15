"""Handle an outbound All-Link Broadcast message to a group."""

from abc import ABCMeta

from ...constants import MessageFlagType
from .. import ack_handler, all_link_cleanup_ack_handler, all_link_cleanup_nak_handler
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

    # pylint: disable=arguments-differ
    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
        await super().async_handle_ack(cmd1=cmd1, cmd2=cmd2, user_data=user_data)

    @all_link_cleanup_ack_handler
    def handle_all_link_ack(self, target, cmd1, cmd2, user_data, hops_left):
        """Handle the All-LInk Command ACK."""
        pass

    @all_link_cleanup_nak_handler
    def handle_all_link_nak(self, target, cmd1, cmd2, user_data, hops_left):
        """Handle the All-LInk Command NAK."""
        pass
