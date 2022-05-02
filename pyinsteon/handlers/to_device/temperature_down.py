"""Thermostat temperature up command."""
from ...topics import THERMOSTAT_TEMPERATURE_DOWN
from .. import ack_handler
from .direct_command import DirectCommandHandlerBase


class TemperatureDownCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_TEMPERATURE_DOWN command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_TEMPERATURE_DOWN, address=address)
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
        return await super().async_handle_ack(cmd1, cmd2, user_data)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(degrees=self._degrees, zone=self._zone)
        self._zone = None
        self._degrees = None
