"""Thermostat status manager."""
import asyncio
import logging
from collections import namedtuple

from ..address import Address
from ..constants import ResponseStatus
from ..handlers.from_device.thermostat_set_point_response import (
    ThermostatSetPointResponseHandler,
)
from ..handlers.from_device.thermostat_status_response import (
    ThermostatStatusResponseHandler,
)
from ..handlers.to_device.extended_get_2 import ExtendedGet2Command
from ..handlers.to_device.thermostat_get_set_point import ThermostatGetSetPointCommand
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
        self._response_status = asyncio.Queue()
        self._response_set_point = asyncio.Queue()
        self._status_response.subscribe(self._status_received)
        self._set_point_response.subscribe(self._set_point_received)

    async def async_status(self):
        """Read the device status."""
        status1 = await self._status()
        status2 = await self._set_point()
        return multiple_status(status1, status2)

    async def _status(self):
        """Send the status command and call set point command."""
        while not self._response_status.empty():
            self._response_status.get_nowait()
        retries = 3
        response_status = ResponseStatus.FAILURE
        while retries:
            await self._get_status_command.async_send()
            try:
                response_status = await asyncio.wait_for(
                    self._response_status.get(), TIMEOUT
                )
                return response_status
            except asyncio.TimeoutError:
                _LOGGER.debug("Exception _status timed out, retries: %d", retries)
            retries -= 1
        return response_status

    async def _set_point(self):
        """Send the set point command."""
        while not self._response_set_point.empty():
            self._response_set_point.get_nowait()
        retries = 3
        response_set_point = ResponseStatus.FAILURE
        while retries:
            await self._get_set_point_command.async_send()
            try:
                return await asyncio.wait_for(self._response_set_point.get(), TIMEOUT)
            except asyncio.TimeoutError:
                _LOGGER.debug("Set point response timed out")
            retries -= 1
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
        cooling,
        heating,
        celsius,
        heat_set_point,
    ):
        """Notify the read process that the resonse was received."""
        self._response_status.put_nowait(ResponseStatus.SUCCESS)

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
        self._response_set_point.put_nowait(ResponseStatus.SUCCESS)
