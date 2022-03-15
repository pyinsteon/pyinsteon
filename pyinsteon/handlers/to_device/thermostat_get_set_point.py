"""Handle sending a read request for ALDB records."""

from ...address import Address
from ...topics import EXTENDED_GET_SET
from .. import ack_handler
from .direct_command import DirectCommandHandlerBase


class ThermostatGetSetPointCommand(DirectCommandHandlerBase):
    """Handle sending a read request for ALDB records."""

    def __init__(self, address: Address):
        """Init the ReadALDBCommandHandler."""
        super().__init__(topic=EXTENDED_GET_SET, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self):
        """Send Get Operating Flags message asyncronously."""
        # This is not consistant with the 2441TH dev guide
        # It is consistand with 2441ZTH dev guide howerver
        response = await super().async_send(data3=0x01)
        return response

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response.

        Required to ensure only GET requests are triggered.
        """
        if (
            not user_data
            or not user_data["d1"] == 0x00
            or not user_data["d2"] == 0x00
            or not user_data["d3"] == 0x01
        ):
            return
        await super().async_handle_ack(cmd1, cmd2, user_data)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers.

        Just need to notify listeners that the Set Point Response
        shoudl be coming.
        """
        self._call_subscribers()
