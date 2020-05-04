"""Thermostat temperature up command."""
from .. import direct_ack_handler
from ...topics import THERMOSTAT_CONTROL
from ...constants import ThermostatMode
from .direct_command import DirectCommandHandlerBase


class ThermostatModeCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_TEMPERATURE_DOWN command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_CONTROL, address=address)

    # pylint: disable=arguments-differ
    def send(self, mode):
        """Send the OFF command."""
        super().send(mode=mode)

    # pylint: disable=arguments-differ
    async def async_send(self, mode):
        """Send the OFF command async."""
        if mode == ThermostatMode.HEAT:
            send_mode = 0x04
        elif mode == ThermostatMode.COOL:
            send_mode = 0x05
        elif mode == ThermostatMode.AUTO:
            send_mode = 0x06
        elif mode == ThermostatMode.FAN_ALWAYS_ON:
            send_mode = 0x07
        elif mode == ThermostatMode.FAN_AUTO:
            send_mode = 0x08
        elif mode == ThermostatMode.OFF:
            send_mode = 0x09
        return await super().async_send(mode=send_mode)

    @direct_ack_handler
    def handle_direct_ack(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the OFF response direct ACK."""
        if cmd2 == 0x04:
            mode = ThermostatMode.HEAT
        elif cmd2 == 0x05:
            mode = ThermostatMode.COOL
        elif cmd2 == 0x06:
            mode = ThermostatMode.AUTO
        elif cmd2 == 0x07:
            mode = ThermostatMode.FAN_ALWAYS_ON
        elif cmd2 == 0x08:
            mode = ThermostatMode.FAN_AUTO
        elif cmd2 == 0x09:
            mode = ThermostatMode.OFF

        self._call_subscribers(mode=mode)
