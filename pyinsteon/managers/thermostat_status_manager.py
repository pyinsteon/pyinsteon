"""Thermostat status manager."""
import asyncio
import logging
from collections import namedtuple

from ..address import Address
from ..constants import ResponseStatus
from ..handlers.from_device.thermostat_status_response import (
    ThermostatStatusResponseHandler,
)
from ..handlers.to_device.extended_get_2 import ExtendedGet2Command
from ..handlers.to_device.thermostat_get_set_point import ThermostatGetSetPointCommand
from ..handlers.from_device.thermostat_set_point_response import (
    ThermostatSetPointResponseHandler,
)
from ..utils import multiple_status

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 5

PropertyInfo = namedtuple("PropertyInfo", "name group data_field bit set_cmd")


class GetThermostatStatus:
    """Thermostat status manager."""

    def __init__(self, address):
        """Init the GetThermostatStatus class."""
        self._address = Address(address)
        self._get_status_command = ExtendedGet2Command(self._address)
        self._get_set_point_command = ThermostatGetSetPointCommand(self._address)
        self._status_response = ThermostatStatusResponseHandler(self._address)
        self._set_point_response = ThermostatSetPointResponseHandler(self._address)
        self._response_queue = asyncio.Queue()
        self._status_response.subscribe(self._status_received)
        self._set_point_response.subscribe(self._set_point_received)

    async def async_status(self):
        """Read the device status."""
        return await self._status()

    async def _status(self):
        """Send the status command and call set point command."""
        while not self._response_queue.empty():
            self._response_queue.get_nowait()
        response_status = await self._get_status_command.async_send()
        if response_status == ResponseStatus.SUCCESS:
            try:
                response_status = await asyncio.wait_for(
                    self._response_queue.get(), TIMEOUT
                )
                response_set_point = await self._set_point()
                return multiple_status(response_status, response_set_point)
            except asyncio.TimeoutError:
                return ResponseStatus.FAILURE
        return response_status

    async def _set_point(self):
        """Send the set point command."""
        while not self._response_queue.empty():
            self._response_queue.get_nowait()
        response_set_point = await self._get_set_point_command.async_send()
        if response_set_point == ResponseStatus.SUCCESS:
            try:
                return await asyncio.wait_for(self._response_queue.get(), TIMEOUT)
            except asyncio.TimeoutError:
                _LOGGER.debug("Set point response timed out")
                return ResponseStatus.FAILURE
        return response_set_point

    def _status_received(
        self,
        day,
        hour,
        minute,
        second,
        system_mode,
        fan_mode,
        cool_set_point,
        humidity,
        temperature,
        status_flag,
        heat_set_point,
    ):
        """Notify the read process that the resonse was received."""
        self._response_queue.put_nowait(ResponseStatus.SUCCESS)

    def _set_point_received(
        self,
        stage_1_on_minutes,
        humidity_high,
        humidity_low,
        firmwire,
        cool_set_point,
        heat_set_point,
        rf_offset,
    ):
        """Notify read process that the st point response was received."""
        self._response_queue.put_nowait(ResponseStatus.SUCCESS)
