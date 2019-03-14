"""Get Device Info command handler."""

from ... import pub
from ...address import Address


class IdRequest:
    """Get Device ID command handler."""

    def __init__(self, address: Address):
        """Init the IdRequest class."""
        self._address = Address(address)

    def send(self):
        """Send the Get Device ID request."""
        from ...messages.outbound import send_standard
        from ...messages.message_flags import create
        from ...constants import MessageFlagType
        flags = create(MessageFlagType.DIRECT, False)
        msg = send_standard(self._address, flags, 0x10, 0x00)
        topic = 'send.{}.id_request'.format(self._address.id)
        pub.sendMessage(topic, msg=msg)

    def receive_id(self, cat, subcat, firmware):
        """Receive the device ID information."""
        