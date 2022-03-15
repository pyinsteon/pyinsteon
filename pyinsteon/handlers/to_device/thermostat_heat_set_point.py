"""Thermostat temperature up command."""
from ...topics import THERMOSTAT_SET_HEAT_SETPOINT
from .direct_command import DirectCommandHandlerBase


class ThermostatHeatSetPointCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_SET_COOL_SETPOINT command to a device."""

    def __init__(self, address):
        """Init the ThermostatHeatSetPointCommand class."""
        super().__init__(topic=THERMOSTAT_SET_HEAT_SETPOINT, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, degrees):
        """Send the THERMOSTAT_SET_HEAT_SETPOINT command async."""
        return await super().async_send(degrees=degrees)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        self._call_subscribers(degrees=cmd2 * 0.5)
