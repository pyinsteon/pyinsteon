"""Base class to handle Broadcast messages from devices."""
from abc import ABCMeta
from ...address import Address
from ..inbound_base import InboundHandlerBase


class BroadcastCommandHandlerBase(InboundHandlerBase):
    """Base class to handle inbound Broadcast messages."""

    __meta__ = ABCMeta

    def __init__(self, address, command):
        """Init the BroadcastHandlerBase class."""
        self._address = Address(address)
        super().__init__('{}.{}'.format(self._address.id, command))
