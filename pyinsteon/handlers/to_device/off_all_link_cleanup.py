"""Manage outbound OFF All-Link Broadcast command to a device."""

from ...topics import OFF
from .all_link_cleanup_command import AllLinkCleanupCommandHandlerBase


class OffAllLinkCleanupCommand(AllLinkCleanupCommandHandlerBase):
    """Manage outbound OFF All-Link Broadcast command to a device."""

    def __init__(self, address, group):
        """Init the OnLevelCommand class."""
        super().__init__(topic=OFF, address=address, group=group)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        return await super().async_send(group=0, cmd2=self._group)
