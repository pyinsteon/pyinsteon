"""Peek one byte from device memory."""

from ...topics import PEEK
from .direct_command import DirectCommandHandlerBase


class PeekCommand(DirectCommandHandlerBase):
    """Peek one byte command."""

    def __init__(self, address):
        """Init the PeekCommand class."""
        super().__init__(topic=PEEK, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, lsb: int):
        """Send the PEEK command async."""
        return await super().async_send(lsb=lsb)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(value=cmd2)
