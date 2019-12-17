"""Manage outbound ON All-Link Broadcast command to a device."""

from .all_link_cleanup_command import AllLinkCleanupCommandHandlerBase
from ...topics import ON


class OnLevelAllLinkCleanupCommand(AllLinkCleanupCommandHandlerBase):
    """Manage an outbound ON All-Link Broadcast command to a device."""

    def __init__(self, address, group):
        """Init the OnLevelCommand class."""
        super().__init__(topic=ON, address=address, group=group)

    # pylint: disable=arguments-differ, useless-super-delegation
    def send(self):
        """Send the ON command."""
        super().send(on_level=self._group)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the ON command async."""
        # In this case the group number goes in the cmd2 field
        return await super().async_send(on_level=self._group, group=0)
