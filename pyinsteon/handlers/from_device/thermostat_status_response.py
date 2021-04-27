"""Thermostat Status Response Handler."""
import logging

from .. import inbound_handler
from ...address import Address
from ...constants import MessageFlagType, ThermostatMode
from ...topics import THERMOSTAT_STATUS_RESPONSE
from ...utils import build_topic, calc_thermostat_mode, calc_thermostat_temp, bit_is_set
from ..inbound_base import InboundHandlerBase

_LOGGER = logging.getLogger(__name__)

SYS_MODE_MAP = {
    0: ThermostatMode.OFF,
    1: ThermostatMode.AUTO,
    2: ThermostatMode.HEAT,
    3: ThermostatMode.COOL,
}

MODE_MAP_2441V = {
    0: ThermostatMode.OFF,
    1: ThermostatMode.HEAT,
    2: ThermostatMode.COOL,
    3: ThermostatMode.AUTO,
}

FAN_MAP_2441V = {
    0: ThermostatMode.FAN_AUTO,
    16: ThermostatMode.FAN_ALWAYS_ON,
}


def _parse_status_flag(status_flag):
    """Parse the status flag."""
    cooling = bit_is_set(status_flag, 0)
    heating = bit_is_set(status_flag, 1)
    energy = bit_is_set(status_flag, 2)
    celcius = bit_is_set(status_flag, 3)
    hold = bit_is_set(status_flag, 4)
    return (cooling, heating, energy, celcius, hold)


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
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
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
        cooling, heating, _, celsius, _ = _parse_status_flag(user_data["d11"])
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
            cooling=cooling,
            heating=heating,
            celsius=celsius,
            heat_set_point=heat_set_point,
        )

class ThermostatStatusResponseHandler2441V(InboundHandlerBase):
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
    def handle_response(self, cmd1, cmd2, target, user_data, hops_left):
        """Handle the Status Response from a Thermostat."""
        system_mode = MODE_MAP_2441V.get(user_data["d3"])
        humidity = user_data["d4"]
        temperature = user_data["d5"] / 2
        cool_set_point = user_data["d6"]
        heat_set_point = user_data["d7"]
        fan_mode = FAN_MAP_2441V.get(user_data["d9"])
        self._call_subscribers(
            humidity=humidity,
            temperature=temperature,
            cool_set_point=cool_set_point,
            heat_set_point=heat_set_point,
            fan_mode = fan_mode,
            system_mode=system_mode,
            heating=False,
            celsius=False,
            cooling=False,
        )