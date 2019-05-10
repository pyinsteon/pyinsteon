"""Handle sending a read request for ALDB records."""
import asyncio
import logging

from .. import direct_ack_handler
from ...address import Address
from ...topics import EXTENDED_READ_WRITE_ALDB
from .direct_command import DirectCommandHandlerBase
from ...constants import AllLinkMode

_LOGGER = logging.getLogger(__name__)

class WriteALDBCommandHandler(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(address, EXTENDED_READ_WRITE_ALDB)

    #pylint: disable=arguments-differ
    def send(self, mem_addr: int, mode: AllLinkMode, group: int, target: Address,
             data1: int = 0x00, data2: int = 0x00, data3: int = 0x00, in_use=True):
        """Send ALDB write message."""
        super().send(action=0x02, mem_addr=mem_addr, mode=mode, group=group, target=target,
                     data1=data1, data2=data2, data3=data3, in_use=in_use)

    #pylint: disable=arguments-differ
    async def async_send(self, mem_addr: int, mode: AllLinkMode, group: int, target: Address,
                         data1: int = 0x00, data2: int = 0x00, data3: int = 0x00, in_use=True):
        """Send ALDB write message asyncronously."""
        super().send(action=0x02, mem_addr=mem_addr, mode=mode, group=group, target=target,
                     data1=data1, data2=data2, data3=data3, in_use=in_use)
