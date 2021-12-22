"""Send an All-Link Cleanup ACK message to a device."""

from ...constants import MessageFlagType
from .direct_command import DirectCommandHandlerBase


class AllLinkCleanupAckCommandHandlerBase(DirectCommandHandlerBase):
    """Abstract base class for outbound All-Link Cleanup ACK message handling."""

    def __init__(self, topic, address, group):
        """Init the DirectCommandHandlerBase class."""
        super().__init__(
            topic=topic,
            address=address,
            group=group,
            message_type=MessageFlagType.ALL_LINK_CLEANUP_ACK,
        )

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(**kwargs)
