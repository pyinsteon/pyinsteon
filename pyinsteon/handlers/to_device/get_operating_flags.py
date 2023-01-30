"""Handle sending a read request for ALDB records."""

from ...address import Address
from ...topics import GET_OPERATING_FLAGS
from .direct_command import DirectCommandHandlerBase


class GetOperatingFlagsCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the GetOperatingFlagsCommand."""
        super().__init__(topic=GET_OPERATING_FLAGS, address=address)
        self._group = None

    # pylint: disable=arguments-differ
    async def async_send(self, flags_requested=0, extended=False):
        """Send Get Operating Flags message asyncronously."""
        self._group = flags_requested
        return await super().async_send(flags_requested=self._group, extended=extended)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(group=self._group, flags=cmd2)
        self._group = None
