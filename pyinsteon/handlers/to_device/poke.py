"""Peek one byte from device memory."""

from ...topics import POKE_ONE_BYTE
from .direct_command import DirectCommandHandlerBase


class PokeCommand(DirectCommandHandlerBase):
    """Poke one byte command."""

    def __init__(self, address):
        """Init the PokeCommand class."""
        super().__init__(topic=POKE_ONE_BYTE, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, value: int):
        """Send the POKE command async."""
        return await super().async_send(value=value)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(value=cmd2)
