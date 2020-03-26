"""Manage outbound ON All-Link Broadcast command to a device."""

from ...topics import ON
from .all_link_cleanup_command import AllLinkCleanupCommandHandlerBase


class OnLevelAllLinkCleanupCommand(AllLinkCleanupCommandHandlerBase):
    """Manage an outbound ON All-Link Broadcast command to a device."""

    def __init__(self, address, group):
        """Init the OnLevelCommand class."""
        super().__init__(topic=ON, address=address, group=group)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        # In this case the group number goes in the cmd2 field
        return await super().async_send(on_level=self._group, group=0)
