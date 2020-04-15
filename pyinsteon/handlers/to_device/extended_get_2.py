"""Handle sending a read request for ALDB records."""
import logging

from ...address import Address
from ...topics import EXTENDED_GET_SET_2
from .direct_command import DirectCommandHandlerBase
from .. import direct_ack_handler

_LOGGER = logging.getLogger(__name__)


class ExtendedGet2Command(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_GET_SET_2, address=address)
        self._data1 = 0x00

    # pylint: disable=arguments-differ
    def send(self, group=0):
        """Send Get Operating Flags message."""
        self._data1 = group
        super().send(data1=self._data1)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send Get Operating Flags message asyncronously."""
        return await super().async_send(data1=self._data1)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK."""
        self._call_subscribers()
