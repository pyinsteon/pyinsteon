"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...topics import EXTENDED_READ_WRITE_ALDB
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class ReadALDBCommandHandler(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_READ_WRITE_ALDB, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message asyncronously."""
        return await super().async_send(
            action=0x00, mem_addr=mem_addr, num_recs=num_recs
        )

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(response=0)

    def _update_subscribers_on_nak(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers on DIIRECT NAK received."""
        self._call_subscribers(response=cmd2)

    def _update_subscribers_on_direct_nak(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers on DIIRECT NAK received."""
        self._call_subscribers(response=cmd2)
