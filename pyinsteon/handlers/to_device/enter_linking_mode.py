"""Get Device Info command handler."""
from ...address import Address
from ...topics import ENTER_LINKING_MODE
from ..from_device.assign_to_all_link_group import AssignToAllLinkGroupCommand
from .direct_command import DirectCommandHandlerBase


class EnterLinkingModeCommand(DirectCommandHandlerBase):
    """Place a device in linking mode command handler."""

    def __init__(self, address: Address):
        """Init the IdRequest class."""
        super().__init__(topic=ENTER_LINKING_MODE, address=address)
        self._link_complete_handler = AssignToAllLinkGroupCommand(address)

    # pylint: disable=arguments-differ
    async def async_send(self, group: int = 0):
        """Send the device ID request asyncronously."""
        return await super().async_send(group=group)
