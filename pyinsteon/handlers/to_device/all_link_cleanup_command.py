"""Handle an outbound All-Link Broadcast message to a group."""

from abc import ABCMeta
import asyncio
from ..outbound_base import OutboundHandlerBase
from ...address import Address
from .. import ack_handler, all_link_cleanup_nak_handler, all_link_cleanup_ack_handler
from ...constants import MessageFlagType


class AllLinkCleanupCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound All-Link clean-up message handling."""

    __meta__ = ABCMeta

    def __init__(self, address, command):
        """Init the DirectCommandHandlerBase class."""
        self._address = Address(address)
        self._response_lock = asyncio.Lock()
        msg_type = str(MessageFlagType.ALL_LINK_CLEANUP)
        super().__init__('{}.{}.{}'.format(self._address.id, command, msg_type))
        # We override the _send_topic to ensrue the address does not go as
        # part of the topic. Address is a key word argument for Direct Commands
        self._send_topic = '{}.{}'.format(command, msg_type)

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._address, **kwargs)

    #pylint: disable=arguments-differ
    @ack_handler(wait_response=False)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""

    @all_link_cleanup_ack_handler
    def handle_all_link_ack(self, target, cmd1, cmd2, user_data):
        """Handle the All-LInk Command ACK."""

    @all_link_cleanup_nak_handler
    def handle_all_link_nak(self, target, cmd1, cmd2, user_data):
        """Handle the All-LInk Command NAK."""
