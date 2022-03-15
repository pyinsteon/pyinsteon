"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...constants import ResponseStatus
from ...topics import SET_OPERATING_FLAGS
from ...utils import publish_topic, subscribe_topic, unsubscribe_topic
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class SetOperatingFlagsCommand(DirectCommandHandlerBase):
    """Handle sending a Set Operating Flags command."""

    def __init__(self, address: Address):
        """Init the SetOperatingFlagsCommand."""
        super().__init__(topic=SET_OPERATING_FLAGS, address=address)
        self._nak_topic = f"handler.{self._address.id}.{SET_OPERATING_FLAGS}_nak"

    # pylint: disable=arguments-differ
    async def async_send(self, cmd: int, extended=False):
        """Send Get Operating Flags message asyncronously."""
        cmd_response = await super().async_send(cmd=cmd, extended=extended)
        if cmd_response == ResponseStatus.UNCLEAR and not extended:
            _LOGGER.debug("Attempting resend with extended message")
            cmd_response = await super().async_send(cmd=cmd, extended=True)
        return cmd_response

    def subscribe_direct_nak(self, listener):
        """Subscribe to a direct nak response."""
        subscribe_topic(listener=listener, topic_name=self._nak_topic)

    def unsubscribe_direct_nak(self, listener):
        """Subscribe to a direct nak response."""
        unsubscribe_topic(listener=listener, topic_name=self._nak_topic)

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on DIIRECT NAK received."""
        publish_topic(self._nak_topic, response=cmd2)
