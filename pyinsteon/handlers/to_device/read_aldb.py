"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...topics import EXTENDED_READ_WRITE_ALDB
from ...utils import publish_topic, subscribe_topic, unsubscribe_topic
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class ReadALDBCommandHandler(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_READ_WRITE_ALDB, address=address)
        self._nak_topic = f"handler.{self._address.id}.{EXTENDED_READ_WRITE_ALDB}_nak"

    # pylint: disable=arguments-differ
    def send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message."""
        super().send(mem_addr=mem_addr, num_recs=num_recs)

    # pylint: disable=arguments-differ
    async def async_send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message asyncronously."""
        return await super().async_send(
            action=0x00, mem_addr=mem_addr, num_recs=num_recs
        )

    def subscribe_direct_nak(self, listener):
        """Subscribe to a direct nak response."""
        subscribe_topic(listener=listener, topic_name=self._nak_topic)

    def unsubscribe_direct_nak(self, listener):
        """Subscribe to a direct nak response."""
        unsubscribe_topic(listener=listener, topic_name=self._nak_topic)

    def _update_subscribers(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(ack_response=cmd2)

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on DIIRECT NAK received."""
        publish_topic(self._nak_topic, response=cmd2)
