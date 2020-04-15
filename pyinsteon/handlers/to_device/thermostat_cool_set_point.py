"""Thermostat temperature up command."""
from .. import direct_ack_handler
from ...topics import THERMOSTAT_SET_COOL_SETPOINT
from .direct_command import DirectCommandHandlerBase


class ThermostatCoolSetPointCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_SET_COOL_SETPOINT command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_SET_COOL_SETPOINT, address=address)

    # pylint: disable=arguments-differ
    def send(self, degrees):
        """Send the THERMOSTAT_SET_COOL_SETPOINT command."""
        super().send(degrees=degrees)

    # pylint: disable=arguments-differ
    async def async_send(self, degrees):
        """Send the THERMOSTAT_SET_COOL_SETPOINT command async."""
        return await super().async_send(degrees=degrees)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF response direct ACK."""
        self._call_subscribers(degrees=cmd2 * 0.5)
