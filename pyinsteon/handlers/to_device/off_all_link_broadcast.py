"""Manage outbound OFF All-Link Broadcast command to a device."""

from ...topics import OFF
from .all_link_broadcast_command import AllLinkBroadcastCommandHandlerBase


class OffAllLinkBroadcastCommand(AllLinkBroadcastCommandHandlerBase):
    """Manage outbound OFF All-Link Broadcast command to a device."""

    def __init__(self, group):
        """Init the OnLevelCommand class."""
        super().__init__(topic=OFF, group=group)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send(group=0)
