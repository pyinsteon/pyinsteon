"""Thermostat temperature up command."""
from .. import direct_ack_handler
from ...topics import THERMOSTAT_SET_COOL_SETPOINT
from .direct_command import DirectCommandHandlerBase


class ThermostatCoolSetPointCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_SET_COOL_SETPOINT command to a device."""

    def __init__(self, address, celsius):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_SET_COOL_SETPOINT, address=address)
        self._celsius = celsius

    # pylint: disable=arguments-differ
    def send(self, degrees):
        """Send the OFF command."""
        if hasattr(self._celsius, "value"):
            celsius = self._celsius.value
        else:
            celsius = self._celsius

        super().send(degrees=degrees, celsuis=celsius)

    # pylint: disable=arguments-differ
    async def async_send(self, degrees):
        """Send the OFF command async."""
        if hasattr(self._celsius, "value"):
            celsius = self._celsius.value
        else:
            celsius = self._celsius
        return await super().async_send(degrees=degrees, celsuis=celsius)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data):
        """Handle the OFF response direct ACK."""
        self._call_subscribers(degrees=cmd2 * 0.5)
