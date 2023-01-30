"""Thermostat temperature up command."""
import asyncio

from .. import ack_handler
from ...topics import THERMOSTAT_SET_COOL_SETPOINT
from .direct_command import DirectCommandHandlerBase


class ThermostatCoolSetPointCommand(DirectCommandHandlerBase):
    """Manage an outbound THERMOSTAT_SET_COOL_SETPOINT command to a device."""

    def __init__(self, address):
        """Init the TemperatureUpCommand class."""
        super().__init__(topic=THERMOSTAT_SET_COOL_SETPOINT, address=address)
        self._degrees = None
        self._zone = None
        self._deadband = None

    # pylint: disable=arguments-differ
    async def async_send(self, degrees, zone: int = None, deadband: int = None):
        """Send the THERMOSTAT_SET_COOL_SETPOINT command async."""
        return await super().async_send(degrees=degrees, zone=zone, deadband=deadband)

    @ack_handler
    async def async_handle_ack(self, cmd1, cmd2, user_data):
        """Handle the ACK response."""
        if user_data["d1"]:
            self._degrees = user_data["d1"] / 2
            self._zone = cmd2
            self._deadband = user_data["d2"] / 2
        else:
            self._degrees = cmd2 / 2
            self._zone = None
            self._deadband = None
        await super().async_handle_ack(cmd1=cmd1, cmd2=cmd2, user_data=user_data)
        await asyncio.sleep(0.2)
        self._degrees = None
        self._zone = None
        self._deadband = None

    def _update_subscribers_on_direct_ack(
        self, cmd1, cmd2, target, user_data, hops_left
    ):
        """Update subscribers."""
        self._call_subscribers(
            degrees=self._degrees, zone=self._zone, deadband=self._deadband
        )
