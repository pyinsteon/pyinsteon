"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...constants import ResponseStatus
from ...topics import SET_OPERATING_FLAGS
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class SetOperatingFlagsCommand(DirectCommandHandlerBase):
    """Handle sending a Set Operating Flags command."""

    def __init__(self, address: Address):
        """Init the SetOperatingFlagsCommand."""
        super().__init__(topic=SET_OPERATING_FLAGS, address=address)

    # pylint: disable=arguments-differ
    def send(self, cmd: int, extended=False):
        """Send Get Operating Flags message."""
        super().send(cmd=cmd, extended=extended)

    # pylint: disable=arguments-differ
    async def async_send(self, cmd: int, extended=False):
        """Send Get Operating Flags message asyncronously."""
        cmd_response = await super().async_send(cmd=cmd, extended=extended)
        if cmd_response == ResponseStatus.UNCLEAR and not extended:
            _LOGGER.debug("Attempting resend with extended message")
            cmd_response = await super().async_send(cmd=cmd, extended=True)
        return cmd_response

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on NAK received."""
        self._call_subscribers(response=cmd2)
