"""Get Device Info command handler."""
from .. import pub
from .direct_command import DirectCommandHandlerBase
from ..constants import ResponseStatus
from ..address import Address
from ..topics import ID_REQUEST, ASSIGN_TO_ALL_LINK_GROUP


class IdRequestCommand(DirectCommandHandlerBase):
    """Get Device ID command handler."""

    def __init__(self, address: Address):
        """Init the IdRequest class."""
        super().__init__(address, ID_REQUEST)
        self._id_response_topic = '{}.{}.broadcast'.format(
            self._address.id, ASSIGN_TO_ALL_LINK_GROUP)

    #pylint: disable=arguments-differ
    async def async_send(self):
        """Send the device ID request asyncronously."""
        pub.subscribe(self.receive_id, self._id_response_topic)
        return await super().async_send()

    def handle_direct_ack(self, cmd2, target, user_data):
        """Handle the direct ACK.

        This does not actually do anything and is never called.
        It overrides the base `handle_direct_ack` method in order
        to prevent the response from returning TRUE until the
        ASSIGN_TO_ALL_LINK_GROUP broadcast message is received.
        """

    def receive_id(self, cmd2, target, user_data):
        """Receive the device ID information."""
        if not self.response_lock.locked():
            # Get ID Request not called therefore
            # this is not meant for us
            return

        cat = target.high
        subcat = target.middle
        firmware = target.low
        for subscriber in self._subscribers:
            subscriber(self._address, cat, subcat, firmware)
        pub.unsubscribe(self.receive_id, self._id_response_topic)
        if self.response_lock.locked():
            self.message_response.put_nowait(ResponseStatus.SUCCESS)
        