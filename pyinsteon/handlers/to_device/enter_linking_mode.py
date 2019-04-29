"""Get Device Info command handler."""
from ..direct_command import DirectCommandHandlerBase
from ...address import Address
from ...topics import ENTER_LINKING_MODE
from ..assign_to_all_link_group import AssignToAllLinkGroupCommand


class EnterLinkingModeCommand(DirectCommandHandlerBase):
    """Place a device in linking mode command handler."""

    def __init__(self, address: Address):
        """Init the IdRequest class."""
        super().__init__(address, ENTER_LINKING_MODE)
        self._link_complete_handler = AssignToAllLinkGroupCommand(address)
        # self._id_response_topic = '{}.{}.broadcast'.format(
        #     self._address.id, ASSIGN_TO_ALL_LINK_GROUP)

    #pylint: disable=arguments-differ
    async def async_send(self, group: int = 0):
        """Send the device ID request asyncronously."""
        # pub.subscribe(self.receive_id, self._id_response_topic)
        return await super().async_send(group=group)
