"""Manage outbound ON command to a device."""

from ...topics import ON_FAST
from .direct_command import DirectCommandHandlerBase


class OnFastCommand(DirectCommandHandlerBase):
    """Manage an outbound ON command to a device."""

    def __init__(self, address, group):
        """Init the OnFastCommand class."""
        super().__init__(topic=ON_FAST, address=address, group=group)

    # pylint: disable=arguments-differ
    async def async_send(self, on_level=0xFF):
        """Send the ON FAST command async."""
        return await super().async_send(on_level=on_level, group=self._group)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(on_level=cmd2 if cmd2 else 0xFF)
