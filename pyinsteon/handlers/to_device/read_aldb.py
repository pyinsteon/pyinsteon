"""Handle sending a read request for ALDB records."""
import logging
from .direct_command import DirectCommandHandlerBase
from ...topics import EXTENDED_READ_WRITE_ALDB
from ...address import Address


_LOGGER = logging.getLogger(__name__)

class ReadALDBCommandHandler(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(address, EXTENDED_READ_WRITE_ALDB)

    #pylint: disable=arguments-differ
    def send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message."""
        super().send(mem_addr=mem_addr, num_recs=num_recs)

    #pylint: disable=arguments-differ
    async def async_send(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Send ALDB read message asyncronously."""
        await super().async_send(action=0x00, mem_addr=mem_addr, num_recs=num_recs)
