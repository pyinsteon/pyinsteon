"""Handle sending a read request for ALDB records."""

from ...address import Address
from ...topics import GET_OPERATING_FLAGS
from ...utils import publish_topic, subscribe_topic, unsubscribe_topic
from .direct_command import DirectCommandHandlerBase


class GetOperatingFlagsCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=GET_OPERATING_FLAGS, address=address)
        self._group = None
        self._nak_topic = f"handler.{self._address.id}.{GET_OPERATING_FLAGS}_nak"

    # pylint: disable=arguments-differ
    async def async_send(self, flags_requested=0, extended=False):
        """Send Get Operating Flags message asyncronously."""
        self._group = flags_requested
        return await super().async_send(flags_requested=self._group, extended=extended)

    def subscribe_direct_nak(self, listener):
        """Subscribe to a direct nak response."""
        subscribe_topic(listener=listener, topic_name=self._nak_topic)

    def unsubscribe_direct_nak(self, listener):
        """Subscribe to a direct nak response."""
        unsubscribe_topic(listener=listener, topic_name=self._nak_topic)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(group=self._group, flags=cmd2)
        self._group = None

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on DIRECT NAK received."""
        publish_topic(self._nak_topic, response=cmd2)
