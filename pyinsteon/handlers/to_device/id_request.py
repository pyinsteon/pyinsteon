"""Get Device Info command handler."""
from .direct_command import DirectCommandHandlerBase
from ...address import Address
from ...topics import ID_REQUEST


class IdRequestCommand(DirectCommandHandlerBase):
    """Get Device ID command handler."""

    def __init__(self, address: Address):
        """Init the IdRequest class."""
        super().__init__(address, ID_REQUEST)

    #pylint: disable=arguments-differ
    #pylint: disable=useless-super-delegation
    def send(self):
        """Send the Device ID request."""
        super().send()

    #pylint: disable=arguments-differ
    async def async_send(self):
        """Send the device ID request asyncronously."""
        return await super().async_send()
