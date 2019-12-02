"""Send an All-Link Cleanup ACK message to a device."""

import asyncio
from ..outbound_base import OutboundHandlerBase
from ...address import Address
from .. import ack_handler
from ...constants import MessageFlagType


class AllLinkCleanupAckCommandHandlerBase(OutboundHandlerBase):
    """Abstract base class for outbound All-Link Cleanup ACK message handling."""

    def __init__(self, address, group, command):
        """Init the DirectCommandHandlerBase class."""
        self._address = Address(address)
        self._group = group
        self._response_lock = asyncio.Lock()
        msg_type = str(MessageFlagType.ALL_LINK_CLEANUP_ACK)
        super().__init__(
            "{}.{}.{}.{}".format(self._address.id, command, group, msg_type)
        )
        # We override the _send_topic to ensrue the address does not go as
        # part of the topic. Address is a key word argument for Direct Commands
        self._send_topic = "{}.{}".format(command, msg_type)

    async def async_send(self, **kwargs):
        """Send the command and wait for a direct_nak."""
        return await super().async_send(address=self._address, **kwargs)

    # pylint: disable=arguments-differ
    @ack_handler(wait_response=False)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the message ACK."""
