"""Manage outbound OFF All-Link Broadcast command to a device."""

from .all_link_broadcast_command import AllLinkBroadcastCommandHandlerBase
from ...topics import ON


class OnLevelAllLinkBroadcastCommand(AllLinkBroadcastCommandHandlerBase):
    """Manage outbound OFF All-Link Broadcast command to a device."""

    def __init__(self, group):
        """Init the OnLevelCommand class."""
        super().__init__(topic=ON, group=group)

    # pylint: disable=arguments-differ
    def send(self):
        """Send the ON command."""
        super().send(group=0, on_level=0xFF)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send(group=0, on_level=0xFF)
