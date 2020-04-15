"""Handle sending a read request for ALDB records."""
import logging

from .. import ack_handler, direct_ack_handler
from ...address import Address
from ...topics import EXTENDED_GET_SET
from .direct_command import DirectCommandHandlerBase

_LOGGER = logging.getLogger(__name__)


class ThermostatGetSetPointCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_GET_SET, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send Get Operating Flags message asyncronously."""
        response = await super().async_send(data3=0x01)
        return response

    @ack_handler(wait_response=True)
    def handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response.

        Required to ensure only GET requests are triggered.
        """
        if (
            not user_data
            or not user_data["data1"] == 0x00
            or not user_data["data2"] == 0x00
            or not user_data["data3"] == 0x01
        ):
            return
        super().handle_ack(cmd1, cmd2, user_data)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the direct ACK.

        Just need to notify listeners that the Set Point Response
        shoudl be coming.
        """
        self._call_subscribers()
