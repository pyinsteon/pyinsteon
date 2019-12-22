"""Base class to handle Broadcast messages from devices."""
from ...address import Address
from ..inbound_base import InboundHandlerBase
from ...constants import MessageFlagType


class BroadcastCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound Broadcast messages."""

    def __init__(self, topic, address, group=None):
        """Init the BroadcastHandlerBase class."""
        self._address = Address(address)
        self._group = group
        super().__init__(
            topic=topic,
            address=self._address,
            group=self._group,
            message_type=MessageFlagType.ALL_LINK_BROADCAST,
        )
