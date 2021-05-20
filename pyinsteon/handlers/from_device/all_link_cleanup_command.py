"""Base class to handle Broadcast messages from devices."""

from ...constants import MessageFlagType
from ..inbound_base import InboundHandlerBase


class AllLinkCleanupCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound All-Link Cleanup messages."""

    def __init__(self, topic, address, group):
        """Init the broadcast_handlerBase class."""

        super().__init__(
            topic=topic,
            address=address,
            group=group,
            message_type=MessageFlagType.ALL_LINK_CLEANUP,
        )
