"""Handle sending a read request for ALDB records."""
import logging

from .. import ack_handler
from ...address import Address
from ...topics import EXTENDED_GET_SET
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class ExtendedGetCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address, cmd2=0x00, data1=None, data2=0x00, data3=None):
        """Init the ExtendedGetCommand."""
        super().__init__(topic=EXTENDED_GET_SET, address=address)
        self._cmd2 = cmd2
        self._data1 = data1
        self._data2 = data2
        self._data3 = data3

    # pylint: disable=arguments-differ
    async def async_send(self, group=0, crc=False):
        """Send Get Operating Flags message asyncronously."""
        self._data1 = group
        response = await super().async_send(
            cmd2=self._cmd2,
            data1=self._data1,
            data2=self._data2,
            data3=self._data3,
            crc=crc,
        )
        self._data1 = None
        return response

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response.

        Required to ensure only GET requests are triggered.
        """
        # pylint: disable=too-many-boolean-expressions
        if (
            cmd2 == self._cmd2
            and (self._data1 is None or user_data["d1"] == self._data1)
            and (self._data2 is None or user_data["d2"] == self._data2)
            and (self._data3 is None or user_data["d3"] == self._data3)
        ):
            await super().async_handle_ack(cmd1=cmd1, cmd2=cmd2, user_data=user_data)
