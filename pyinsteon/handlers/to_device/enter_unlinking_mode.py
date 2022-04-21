"""Get Device Info command handler."""
from ...address import Address
from ...topics import ENTER_UNLINKING_MODE
from .direct_command import DirectCommandHandlerBase


class EnterUnlinkingModeCommand(DirectCommandHandlerBase):
    """Place a device in linking mode command handler."""

    def __init__(self, address: Address):
        """Init the EnterUnlinkingModeCommand class."""
        super().__init__(topic=ENTER_UNLINKING_MODE, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, group: int = 0, extended: bool = False):
        """Send the ENTER_UNLINKING_MODE request asyncronously."""
        return await super().async_send(group=group, extended=extended)
