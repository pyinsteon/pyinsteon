"""Thermostat temperature up command."""
from ...constants import ThermostatMode
from ...topics import THERMOSTAT_CONTROL
from .direct_command import DirectCommandHandlerBase

MODE_MAP = {
    ThermostatMode.HEAT: 0x04,
    ThermostatMode.COOL: 0x05,
    ThermostatMode.AUTO: 0x06,
    ThermostatMode.FAN_ALWAYS_ON: 0x07,
    ThermostatMode.FAN_AUTO: 0x08,
    ThermostatMode.OFF: 0x09,
}

THERMOSTAT_MODE_MAP = {
    0x04: ThermostatMode.HEAT,
    0x05: ThermostatMode.COOL,
    0x06: ThermostatMode.AUTO,
    0x07: ThermostatMode.FAN_ALWAYS_ON,
    0x08: ThermostatMode.FAN_AUTO,
    0x09: ThermostatMode.OFF,
}


class ThermostatModeCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_TEMPERATURE_DOWN command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_CONTROL, address=address)

    # pylint: disable=arguments-differ
    async def async_send(self, thermostat_mode):
        """Send the OFF command async."""
        thermostat_mode = ThermostatMode(thermostat_mode)
        send_mode = MODE_MAP.get(thermostat_mode)
        if send_mode is None:
            raise ValueError("Invalid thermostat mode")
        return await super().async_send(thermostat_mode=send_mode)

    def _update_subscribers_on_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Update subscribers."""
        thermostat_mode = THERMOSTAT_MODE_MAP.get(cmd2)
        if thermostat_mode is None:
            return
        self._call_subscribers(thermostat_mode=thermostat_mode)
