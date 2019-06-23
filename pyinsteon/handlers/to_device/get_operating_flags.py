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
        super().__init__(address, GET_OPERATING_FLAGS)

    #pylint: disable=arguments-differ
    def send(self, flags_requested=0):
        """Send Get Operating Flags message."""
        super().send(flags_requested=flags_requested)

    #pylint: disable=arguments-differ
    async def async_send(self, flags_requested=0):
        """Send Get Operating Flags message asyncronously."""
        result = await super().async_send(flags_requested=0)
        return result

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the direct ACK message."""
        self._call_subscribers(flags=cmd2)
