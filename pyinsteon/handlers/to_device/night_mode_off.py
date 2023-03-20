"""Manage outbound ON command to a device."""

from ...topics import NIGHT_MODE_OFF
from .direct_command import DirectCommandHandlerBase


class NightModeOffCommand(DirectCommandHandlerBase):
    """Manage an outbound NIGHT_MODE_OFF command to a device."""

    def __init__(self, address):
        """Init the NightModeOffCommand class."""
        super().__init__(topic=NIGHT_MODE_OFF, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send the NIGHT_MODE_OFF command async."""
        return await super().async_send()

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(night_mode=False)
