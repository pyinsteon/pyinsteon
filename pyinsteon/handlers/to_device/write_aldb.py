"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...topics import EXTENDED_READ_WRITE_ALDB
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class WriteALDBCommandHandler(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_READ_WRITE_ALDB, address=address)

    # pylint: disable=arguments-differ
    async def async_send(
        self,
        mem_addr: int,
        controller: bool,
        group: int,
        target: Address,
        data1: int = 0x00,
        data2: int = 0x00,
        data3: int = 0x00,
        in_use: bool = True,
        high_water_mark: bool = False,
        bit5: int = 0,
        bit4: int = 0,
    ):
        """Send ALDB write message asyncronously."""
        return await super().async_send(
            action=0x02,
            mem_addr=mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            in_use=in_use,
            high_water_mark=high_water_mark,
            bit5=bit5,
            bit4=bit4,
        )
