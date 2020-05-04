"""Thermostat temperature up command."""
from .. import direct_ack_handler
from ...topics import THERMOSTAT_TEMPERATURE_DOWN
from .direct_command import DirectCommandHandlerBase


class TemperatureDownCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_TEMPERATURE_DOWN command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_TEMPERATURE_DOWN, address=address)

    # pylint: disable=arguments-differ
    def send(self, degrees=1):
        """Send the OFF command."""
        super().send(degrees=degrees)

    # pylint: disable=arguments-differ
    async def async_send(self, degrees=1):
        """Send the OFF command async."""
        return await super().async_send(degrees=degrees)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF response direct ACK."""
        self._call_subscribers(degrees=cmd2 * 0.5)
