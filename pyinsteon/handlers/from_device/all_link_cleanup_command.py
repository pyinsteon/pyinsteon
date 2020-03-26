"""Base class to handle Broadcast messages from devices."""
from ...address import Address
from ...constants import MessageFlagType
from ..inbound_base import InboundHandlerBase


class AllLinkCleanupCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound All-Link Cleanup messages."""

    def __init__(self, topic, address, group):
        """Init the BroadcastHandlerBase class."""
        self._address = Address(address)
        self._group = group
        super().__init__(
            topic=topic,
            address=self._address,
            group=self._group,
            message_type=MessageFlagType.ALL_LINK_CLEANUP,
        )
