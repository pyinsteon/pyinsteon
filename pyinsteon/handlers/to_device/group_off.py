"""Manage outbound ON command to a device."""

from ...topics import GROUP_OFF
from .direct_command import DirectCommandHandlerBase


class GroupOffCommand(DirectCommandHandlerBase):
    """Manage an outbound GROUP OFF command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(topic=GROUP_OFF, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, group: int):
        """Send the GROUP OFF command async."""
        return await super().async_send(group=group)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(group=cmd2)
