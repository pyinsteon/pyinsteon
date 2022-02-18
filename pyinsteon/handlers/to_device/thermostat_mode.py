"""Thermostat temperature up command."""
from ...constants import ThermostatMode
from ...topics import THERMOSTAT_CONTROL
from .direct_command import DirectCommandHandlerBase


class ThermostatModeCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_TEMPERATURE_DOWN command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_CONTROL, address=address)

    # pylint: disable=arguments-differ
    def send(self, thermostat_mode):
        """Send the OFF command."""
        super().send(thermostat_mode=thermostat_mode)

    # pylint: disable=arguments-differ
    async def async_send(self, thermostat_mode):
        """Send the OFF command async."""
        if thermostat_mode == ThermostatMode.HEAT:
            send_mode = 0x04
        elif thermostat_mode == ThermostatMode.COOL:
            send_mode = 0x05
        elif thermostat_mode == ThermostatMode.AUTO:
            send_mode = 0x06
        elif thermostat_mode == ThermostatMode.FAN_ALWAYS_ON:
            send_mode = 0x07
        elif thermostat_mode == ThermostatMode.FAN_AUTO:
            send_mode = 0x08
        elif thermostat_mode == ThermostatMode.OFF:
            send_mode = 0x09
        return await super().async_send(thermostat_mode=send_mode)

    def _update_subscribers(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        if cmd2 == 0x04:
            thermostat_mode = ThermostatMode.HEAT
        elif cmd2 == 0x05:
            thermostat_mode = ThermostatMode.COOL
        elif cmd2 == 0x06:
            thermostat_mode = ThermostatMode.AUTO
        elif cmd2 == 0x07:
            thermostat_mode = ThermostatMode.FAN_ALWAYS_ON
        elif cmd2 == 0x08:
            thermostat_mode = ThermostatMode.FAN_AUTO
        elif cmd2 == 0x09:
            thermostat_mode = ThermostatMode.OFF

        self._call_subscribers(thermostat_mode=thermostat_mode)
