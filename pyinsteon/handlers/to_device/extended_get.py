"""Handle sending a read request for ALDB records."""
import logging

from .. import ack_handler
from ...address import Address
from ...topics import EXTENDED_GET_SET
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class ExtendedGetCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_GET_SET, address=address)
        self._data1 = None
        self._data2 = 0x00

    # pylint: disable=arguments-differ
    def send(self, group=0):
        """Send Get Operating Flags message."""
        self._data1 = group
        super().send(data1=self._data1, data2=self._data2)

    # pylint: disable=arguments-differ
    async def async_send(self, group=0):
        """Send Get Operating Flags message asyncronously."""
        self._data1 = group
        response = await super().async_send(data1=self._data1, data2=self._data2)
        self._data1 = None
        return response

    @ack_handler(wait_response=True)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response.

        Required to ensure only GET requests are triggered.
        """
        if (
            not user_data
            or not user_data["data1"] == self._data1
            or not user_data["data2"] == self._data2
        ):
            return
        super().handle_ack(cmd1, cmd2, user_data)
