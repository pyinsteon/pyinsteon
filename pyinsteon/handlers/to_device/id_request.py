"""Get Device Info command handler."""
from ...address import Address
from ...topics import ID_REQUEST
from .direct_command import DirectCommandHandlerBase


class IdRequestCommand(DirectCommandHandlerBase):
    """Get Device ID command handler."""

    def __init__(self, address: Address):
        """Init the IdRequest class."""
        super().__init__(topic=ID_REQUEST, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the device ID request asyncronously."""
        return await super().async_send()
