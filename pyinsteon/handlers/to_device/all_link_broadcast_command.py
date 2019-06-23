"""Handle an outbound All-Link Broadcast message to a group."""

import asyncio
from abc import ABCMeta

from ...address import Address
from ...constants import MessageFlagType
from .. import ack_handler
from ..outbound_base import OutboundHandlerBase


class AllLinkBroadcastCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound All-Link broadcast message handling."""

    __meta__ = ABCMeta

    def __init__(self, group, command):
        """Init the DirectCommandHandlerBase class."""
        self._target = Address(bytearray([0x00, 0x00, group]))
        self._response_lock = asyncio.Lock()
        msg_type = str(MessageFlagType.ALL_LINK_BROADCAST)
        super().__init__('{}.{}.{}'.format(self._target.id, command, msg_type))
        # We override the _send_topic to ensrue the address does not go as
        # part of the topic. Address is a key word argument for Direct Commands
        self._send_topic = '{}.{:s}'.format(command, msg_type)

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._target, **kwargs)

    #pylint: disable=arguments-differ
    @ack_handler(wait_response=False)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
