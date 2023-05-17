"""Manage inbound ON command from device."""
import logging

from .. import inbound_handler
from ...constants import MessageFlagType
from ...topics import THERMOSTAT_MODE_STATUS
from ...utils import calc_thermostat_mode
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)


class ThermostatModeHandler(InboundHandlerBase):
    """Heat set point command inbound."""

    arg_spec = {
        "system_mode": "ThermostatMode - Current system mode of the thermostat (heat, cool, off, etc.)",
        "fan_mode": "ThermostatMode - Current fan mode of the thermostat (on, auto, etc.)",
    }

    def __init__(self, address):
        """Init the ThermostatModeHandler class."""
        super().__init__(
            topic=THERMOSTAT_MODE_STATUS,
            address=address,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the thermostat mode response from a device."""
        sys_mode, fan_mode = calc_thermostat_mode(cmd2)
        self._call_subscribers(system_mode=sys_mode, fan_mode=fan_mode)
