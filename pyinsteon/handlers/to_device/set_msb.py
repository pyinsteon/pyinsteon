"""Set most significant byte for peek/poke commands."""
from ...topics import SET_ADDRESS_MSB
from .direct_command import DirectCommandHandlerBase


class SetMsbCommand(DirectCommandHandlerBase):
    """Set most significant byte for peek/poke commands."""

    def __init__(self, address):
        """Init the SetMsbCommand class."""
        super().__init__(topic=SET_ADDRESS_MSB, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, high_byte):
        """Send the ON command async."""
        return await super().async_send(high_byte=high_byte)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(high_byte=cmd2)
