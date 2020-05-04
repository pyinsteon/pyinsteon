"""Handle sending a read request for ALDB records."""
import logging

from .. import direct_ack_handler
from ...address import Address
from ...topics import GET_OPERATING_FLAGS
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class GetOperatingFlagsCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=GET_OPERATING_FLAGS, address=address)
        self._group = None

    # pylint: disable=arguments-differ
    def send(self, flags_requested=0):
        """Send Get Operating Flags message."""
        super().send(flags_requested=flags_requested)

    # pylint: disable=arguments-differ
    async def async_send(self, flags_requested=0):
        """Send Get Operating Flags message asyncronously."""
        self._group = flags_requested
        return await super().async_send(flags_requested=self._group)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK message."""
        self._call_subscribers(group=self._group, flags=cmd2)
        self._group = None
