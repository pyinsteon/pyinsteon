"""Base class to handle Broadcast messages from devices."""
from abc import ABCMeta
from ...address import Address
from ..inbound_base import InboundHandlerBase
from ...constants import MessageFlagType


class AllLinkCleanupAckCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound Broadcast messages."""

    __meta__ = ABCMeta

    def __init__(self, address, command):
        """Init the BroadcastHandlerBase class."""
        self._address = Address(address)
        msg_type = str(MessageFlagType.ALL_LINK_CLEANUP_ACK)
        topic = '{}.{}.{}'.format(self._address.id, command, msg_type)
        super().__init__(topic)
