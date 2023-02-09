"""Thermostat temperature up command."""
from .. import ack_handler
from ...topics import THERMOSTAT_TEMPERATURE_UP
from .direct_command import DirectCommandHandlerBase


class TemperatureUpCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_TEMPERATURE_UP command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_TEMPERATURE_UP, address=address)
        self._degrees = None
        self._zone = None

    # pylint: disable=arguments-differ
    async def async_send(self, degrees=1, zone=None):
        """Send the OFF command async."""
        return await super().async_send(degrees=degrees, zone=zone)

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response."""
        if user_data["d1"]:
            self._zone = cmd2
            self._degrees = user_data["d1"] * 0.5
        else:
            self._zone = None
            self._degrees = cmd2 * 0.5
        return await super().async_handle_ack(cmd1=cmd1, cmd2=cmd2, user_data=user_data)

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(degrees=self._degrees, zone=self._zone)
        self._zone = None
        self._degrees = None
