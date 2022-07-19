"""Manage outbound ON command to a device."""

from ...topics import IO_OUTPUT_OFF
from .direct_command import DirectCommandHandlerBase


class IoOutputOffCommand(DirectCommandHandlerBase):
    """Manage an outbound IO_OUTPUT_ON command to a device."""

    def __init__(self, address):
        """Init the OnLevelCommand class."""
        super().__init__(topic=IO_OUTPUT_OFF, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, output):
        """Send the ON command async."""
        return await super().async_send(output=output)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(output=cmd2, on_level=0xff)
