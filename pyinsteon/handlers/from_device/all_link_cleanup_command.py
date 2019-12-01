"""Base class to handle Broadcast messages from devices."""
from ...address import Address
from ..inbound_base import InboundHandlerBase
from ...constants import MessageFlagType


class AllLinkCleanupCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound All-Link Cleanup messages."""

    def __init__(self, address, group, command):
        """Init the BroadcastHandlerBase class."""
        self._address = Address(address)
        self._group = group
        msg_type = str(MessageFlagType.ALL_LINK_CLEANUP)
        topic = '{}.{}.{}.{}'.format(self._address.id, command, group, msg_type)
        super().__init__(topic)