"""Thermostat status manager."""
import asyncio
from collections import namedtuple
import logging

from ..address import Address
from ..constants import ResponseStatus, ThermostatMode
from ..handlers.from_device.ext_get_response import ExtendedGetResponseHandler
from ..handlers.to_device.extended_get import ExtendedGetCommand
from ..subscriber_base import SubscriberBase
from ..utils import (
    bit_is_set,
    calc_thermostat_mode,
    calc_thermostat_temp,
    multiple_status,
)

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 5
SYS_MODE_MAP = {
    0: ThermostatMode.OFF,
    1: ThermostatMode.AUTO,
    2: ThermostatMode.HEAT,
    3: ThermostatMode.COOL,
}


def _parse_status_flag(status_flag):
    """Parse the status flag."""
    cooling = bit_is_set(status_flag, 0)
    heating = bit_is_set(status_flag, 1)
    energy = bit_is_set(status_flag, 2)
    celcius = bit_is_set(status_flag, 3)
    hold = bit_is_set(status_flag, 4)
    return (cooling, heating, energy, celcius, hold)


PropertyInfo = namedtuple("PropertyInfo", "name group data_field bit set_cmd")


class StatusNotifier(SubscriberBase):
    """Notification class for status messages received."""

    arg_spec = {
        "day": "int - Thermostat current day of the week value.",
        "hour": "int - Thermostat current hour of the day value.",
        "minute": "int - Thermostat current minute of the hour value.",
        "second": "int - Thermostat current second of the minute value.",
        "system_mode": "SystemMode - Thermostat current system mode (heat, cool, etc.).",
        "fan_mode": "SystemMode - Thermostat current system mode (auto, always_on, etc.).",
        "cool_set_point": "int - Thermostat set point in cool mode.",
        "heat_set_point": "int - Thermostat set point in heat mode.",
        "humidity": "int - Thermostat current humidity reading.",
        "temperature": "float - Thermostat current temperature reading.",
        "cooling": "bool - Indicates if the thermostat temperature is above the cool set point.",
        "heating": "bool - Indicates if the thermostat temperature is below the heat set point.",
        "celsius": "bool - Indicates if the thermostat is measuring in celsius (True = celsius, False = fahrenheit).",
    }

    def call_subscribers(
        self,
        day,
        hour,
        minute,
        second,
        system_mode,
        fan_mode,
        cool_set_point,
        heat_set_point,
        humidity,
        temperature,
        cooling,
        heating,
        celsius,
    ):
        """Notify subscribers of the status received message."""
        return super()._call_subscribers(
            day=day,
            hour=hour,
            minute=minute,
            second=second,
            system_mode=system_mode,
            fan_mode=fan_mode,
            cool_set_point=cool_set_point,
            heat_set_point=heat_set_point,
            humidity=humidity,
            temperature=temperature,
            cooling=cooling,
            heating=heating,
            celsius=celsius,
        )


class SetPointNotifier(SubscriberBase):
    """Notification class for set point status updates."""

    arg_spec = {
        "humidity_high": "int - Humidity high set point.",
        "humidity_low": "int - Humidity low set point.",
        "firmwire": "int - Thermostat firmware version.",
        "cool_set_point": "int - Cool set point.",
        "heat_set_point": "int - Heat set point.",
        "rf_offset": "int - Temperature offset for callibration.",
    }

    def call_subscribers(
        self,
        humidity_high,
        humidity_low,
        firmwire,
        cool_set_point,
        heat_set_point,
        rf_offset,
    ):
        """Notify subscribers of set point status updates."""
        self._call_subscribers(
            humidity_high=humidity_high,
            humidity_low=humidity_low,
            firmwire=firmwire,
            cool_set_point=cool_set_point,
            heat_set_point=heat_set_point,
            rf_offset=rf_offset,
        )


class GetThermostatStatus:
    """Thermostat status manager."""

    def __init__(self, address):
        """Init the GetThermostatStatus class."""
        self._address = Address(address)
        self._get_status_command = ExtendedGetCommand(self._address, cmd2=0x02)
        self._get_set_point_command = ExtendedGetCommand(
            address=self._address, cmd2=0x00, data1=0x00, data2=0x00, data3=0x01
        )
        self._status_response = ExtendedGetResponseHandler(
            self._address, cmd2=0x02, data1=0x01, data2=None, data3=None
        )
        self._set_point_response = ExtendedGetResponseHandler(
            self._address, cmd2=0x00, data1=0x00, data2=0x01, data3=0x01
        )
        self._response_status = asyncio.Queue()
        self._response_set_point = asyncio.Queue()
        self._status_response.subscribe(self._status_received)
        self._set_point_response.subscribe(self._set_point_received)

        self._set_point_received_topic = ""
        self._status_listeners = []
        self._set_point_listeners = []
        self._status_notifier = StatusNotifier(
            f"{self._address.id}.thermostat_status_manager.status_received"
        )
        self._set_point_notifier = SetPointNotifier(
            f"{self._address.id}.thermostat_status_manager.set_point_received"
        )

    async def async_status(self):
        """Read the device status."""
        status1 = await self._status()
        status2 = await self._set_point()
        return multiple_status(status1, status2)

    def subscribe_status(self, listener, force_strong_ref=False):
        """Subscribe to status updates."""
        self._status_notifier.subscribe(listener)
        if force_strong_ref and listener not in self._status_listeners:
            self._status_listeners.append(listener)

    def unsubscribe_status(self, listener):
        """Unsubscribe to status updates."""
        self._status_notifier.unsubscribe(listener)
        if listener in self._status_listeners:
            self._status_listeners.pop(listener)

    def subscribe_set_point(self, listener, force_strong_ref=False):
        """Subscribe to set point updates."""
        self._set_point_notifier.subscribe(listener)
        if force_strong_ref and listener not in self._set_point_listeners:
            self._set_point_listeners.append(listener)

    def unsubscribe_set_point(self, listener):
        """Unsubscribe to set point updates."""
        self._set_point_notifier.unsubscribe(listener)
        if listener in self._set_point_listeners:
            self._set_point_listeners.pop(listener)

    async def _status(self):
        """Send the status command and call set point command."""
        while not self._response_status.empty():
            self._response_status.get_nowait()
        retries = 3
        response_status = ResponseStatus.FAILURE
        while retries:
            response = await self._get_status_command.async_send(crc=True)
            if response == ResponseStatus.SUCCESS:
                try:
                    response_status = await asyncio.wait_for(
                        self._response_status.get(), TIMEOUT
                    )
                    return response_status
                except asyncio.TimeoutError:
                    _LOGGER.debug("Exception _status timed out, retries: %d", retries)
            else:
                response_status = response
            retries -= 1
        return response_status

    async def _set_point(self):
        """Send the set point command."""
        while not self._response_set_point.empty():
            self._response_set_point.get_nowait()
        retries = 3
        response_set_point = ResponseStatus.FAILURE
        while retries:
            response = await self._get_set_point_command.async_send(crc=True)
            if response == ResponseStatus.SUCCESS:
                try:
                    return await asyncio.wait_for(
                        self._response_set_point.get(), TIMEOUT
                    )
                except asyncio.TimeoutError:
                    _LOGGER.debug("Set point response timed out")
            else:
                response_set_point = response
            retries -= 1
        return response_set_point

    def _status_received(self, group, data):
        """Notify the read process that the resonse was received."""
        self._response_status.put_nowait(ResponseStatus.SUCCESS)
        day = data["data2"]
        hour = data["data3"]
        minute = data["data4"]
        second = data["data5"]
        system_mode, fan_mode = calc_thermostat_mode(
            data["data6"], SYS_MODE_MAP, sys_low=False
        )
        cool_set_point = data["data7"]
        humidity = data["data8"]
        temp = calc_thermostat_temp(data["data9"], data["data10"])
        cooling, heating, _, celsius, _ = _parse_status_flag(data["data11"])
        heat_set_point = data["data12"]
        self._status_notifier.call_subscribers(
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

    def _set_point_received(self, group, data):
        """Handle the Humidity set point response from a device."""
        humidity_high = data["data4"]
        humidity_low = data["data5"]
        firmwire = data["data6"]
        cool_set_point = data["data7"]
        heat_set_point = data["data8"]
        rf_offset = data["data9"]
        self._set_point_notifier.call_subscribers(
            humidity_high=humidity_high,
            humidity_low=humidity_low,
            firmwire=firmwire,
            cool_set_point=cool_set_point,
            heat_set_point=heat_set_point,
            rf_offset=rf_offset,
        )
        self._response_set_point.put_nowait(ResponseStatus.SUCCESS)
