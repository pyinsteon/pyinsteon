"""Handle sending a read request for ALDB records."""

from ...address import Address
from ...topics import EXTENDED_GET_SET_2
from .direct_command import DirectCommandHandlerBase


class ExtendedGet2Command(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_GET_SET_2, address=address)
        self._data1 = 0x00

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send Get Operating Flags message asyncronously."""
        return await super().async_send(data1=self._data1)
