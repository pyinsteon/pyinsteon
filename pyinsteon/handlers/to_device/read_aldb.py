"""Handle sending a read request for ALDB records."""
import asyncio
import logging

from ... import pub
from ...address import Address
from ...constants import MessageFlagType, ResponseStatus
from ...topics import EXTENDED_READ_WRITE_ALDB, EXTENDED_READ_WRITE_ALDB_DIRECT_NAK
from ...utils import build_topic, subscribe_topic
from .. import direct_ack_handler, direct_nak_handler
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class ReadALDBCommandHandler(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_READ_WRITE_ALDB, address=address)
        direct_nak_topic = build_topic(
            topic=EXTENDED_READ_WRITE_ALDB_DIRECT_NAK,
            address=self._address.id,
            message_type=MessageFlagType.DIRECT_NAK,
        )
        subscribe_topic(self.async_handle_direct_nak, direct_nak_topic)

    # pylint: disable=arguments-differ
    async def async_send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message asyncronously."""
        return await super().async_send(
            action=0x00, mem_addr=mem_addr, num_recs=num_recs
        )

    @direct_ack_handler
    async def async_handle_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left, topic=pub.AUTO_TOPIC
    ):
        """Handle the direct ACK."""
        # Need to make sure the ACK has time to aquire the lock
        await asyncio.sleep(0.05)
        if topic.name.endswith("direct_nak.direct_ack"):
            return
        if self._response_lock.locked():
            await self._direct_response.put(ResponseStatus.SUCCESS)
            self._update_subscribers_on_ack(cmd1, cmd2, target, user_data, hops_left)
            await asyncio.sleep(0.05)

    @direct_nak_handler
    async def async_handle_direct_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the message ACK."""
        # Need to make sure the ACK has time to aquire the lock
        await asyncio.sleep(0.05)
        if self._response_lock.locked():
            await self._direct_response.put(ResponseStatus.FAILURE)
            self._update_subscribers_on_nak(cmd1, cmd2, target, user_data, hops_left)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(response=0)

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on DIIRECT NAK received."""
        self._call_subscribers(response=cmd2)
