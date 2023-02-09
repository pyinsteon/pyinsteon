"""Manage outbound ON command to a device."""

from ...topics import ON
from .direct_command import DirectCommandHandlerBase


class OnLevelCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address, group):
        """Init the OnLevelCommand class."""
        super().__init__(topic=ON, address=address, group=group)

    @property
    def group(self):
        """Command group."""
        return self._group

    # pylint: disable=arguments-differ
    async def async_send(self, on_level=0xFF):
        """Send the ON command async."""
        return await super().async_send(on_level=on_level, group=self._group)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xFF)
