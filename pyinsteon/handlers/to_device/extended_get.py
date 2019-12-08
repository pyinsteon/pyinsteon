"""Handle sending a read request for ALDB records."""
import logging

from .. import direct_ack_handler
from ...address import Address
from ...topics import EXTENDED_GET_SET
from .direct_command import DirectCommandHandlerBase
from ...utils import build_topic
from ...constants import MessageFlagType

_LOGGER = logging.getLogger(__name__)


class ExtendedGetCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address, data1=None, data2=None):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_GET_SET, address=address)
        self._data1 = data1
        self._data2 = data2

    # pylint: disable=arguments-differ
    def send(self):
        """Send Get Operating Flags message."""
        super().send(data1=self._data1, data2=self._data2)

    # pylint: disable=arguments-differ
    async def async_send(self, group=0):
        """Send Get Operating Flags message asyncronously."""
        return await super().async_send(data1=self._data1, data2=self._data2)
