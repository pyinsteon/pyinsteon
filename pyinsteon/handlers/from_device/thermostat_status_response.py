"""Thermostat Status Response Handler."""
import logging

from .. import inbound_handler
from ...address import Address
from ...constants import MessageFlagType, ThermostatMode
from ...topics import THERMOSTAT_STATUS_RESPONSE
from ...utils import build_topic, calc_thermostat_mode, calc_thermostat_temp
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)

SYS_MODE_MAP = {
    0: ThermostatMode.OFF,
    1: ThermostatMode.AUTO,
    2: ThermostatMode.HEAT,
    3: ThermostatMode.COOL,
}


class ThermostatStatusResponseHandler(InboundHandlerBase):
    """Thermostat Status Response Handler."""

    def __init__(self, address):
        """Init the ThermostatStatusResponseHandler class."""
        self._address = Address(address)
        super().__init__(
            topic=THERMOSTAT_STATUS_RESPONSE,
            address=self._address,
            message_type=MessageFlagType.DIRECT,
        )
        self._subscriber_topic = build_topic(
            prefix="handler.{}".format(self._address.id),  # Force address
            topic=THERMOSTAT_STATUS_RESPONSE,
            message_type=MessageFlagType.DIRECT,
        )

    @inbound_handler
    def handle_response(self, cmd1, cmd2, target, user_data):
        """Handle the Status Response from a Thermostat."""
        day = user_data["d2"]
        hour = user_data["d3"]
        minute = user_data["d4"]
        second = user_data["d5"]
        system_mode, fan_mode = calc_thermostat_mode(
            user_data["d6"], SYS_MODE_MAP, sys_low=False
        )
        cool_set_point = user_data["d7"]
        humidity = user_data["d8"]
        temp = calc_thermostat_temp(user_data["d9"], user_data["d10"])
        status_flag = user_data["d11"]
        heat_set_point = user_data["d12"]
        self._call_subscribers(
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            system_mode=system_mode,
            fan_mode=fan_mode,
            cool_set_point=cool_set_point,
            humidity=humidity,
            temperature=temp,
            status_flag=status_flag,
            heat_set_point=heat_set_point,
        )
