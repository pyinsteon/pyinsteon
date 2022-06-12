"""X10 devices."""
import asyncio

from ..constants import ResponseStatus, X10Commands
from ..events import OFF_EVENT, ON_EVENT, Event
from ..groups import DIMMABLE_LIGHT, ON_OFF_SWITCH
from ..groups.on_level import OnLevel
from ..groups.on_off import OnOff
from ..handlers.to_device.x10_send import X10CommandSend
from ..managers.x10_manager import (
    X10AllLightsOnOffManager,
    X10AllUnitsOffManager,
    X10DimBrightenManager,
    X10OnOffManager,
)
from ..utils import multiple_status
from .x10_base import X10DeviceBase

ALL_LIGHTS_ON_OFF = "all_lights_on_off"
ALL_UNITS_OFF = "all_units_off"
DIM_BRIGHT = "dim_bright"


class X10OnOffSensor(X10DeviceBase):
    """X10 On/Off device."""

    def __init__(self, housecode, unitcode):
        """Init the X10OnOffSensor class."""
        super().__init__(housecode, unitcode)
        self._description = "X10 On/Off Sensor"

    def _register_handlers_and_managers(self):
        self._managers[ON_OFF_SWITCH] = X10OnOffManager(self._address)
        self._managers[ALL_UNITS_OFF] = X10AllUnitsOffManager(self._address)

    def _register_groups(self):
        self._groups[1] = OnOff(ON_OFF_SWITCH, self._address, 1)

    def _register_events(self):
        self._events[1] = {}
        self._events[1][ON_EVENT] = Event(ON_EVENT, self._address, group=1)
        self._events[1][OFF_EVENT] = Event(OFF_EVENT, self._address, group=1)

    def _subscribe_to_handelers_and_managers(self):
        self._managers[ON_OFF_SWITCH].subscribe(self._groups[1].set_value)
        self._managers[ALL_UNITS_OFF].subscribe(self._groups[1].set_value)

        self._managers[ON_OFF_SWITCH].subscribe_on(self._events[1][ON_EVENT].trigger)
        self._managers[ON_OFF_SWITCH].subscribe_off(self._events[1][OFF_EVENT].trigger)
        self._managers[ALL_UNITS_OFF].subscribe(self._events[1][OFF_EVENT].trigger)


class X10OnOff(X10OnOffSensor):
    """X10 On/Off device."""

    def __init__(self, housecode, unitcode):
        """Init the X10OnOff class."""
        super().__init__(housecode, unitcode)
        self._description = "X10 On/Off Switch"
        self._on_cmd = X10CommandSend(self._address, X10Commands.ON)
        self._off_cmd = X10CommandSend(self._address, X10Commands.OFF)

    def on(self, group=0):
        """Turn on the switch."""
        asyncio.ensure_future(self.async_on())

    async def async_on(self, group=0):
        """Turn on the switch."""
        retries = 0
        while retries < 3:
            result = await self._on_cmd.async_send()
            if result == ResponseStatus.SUCCESS:
                self._groups[1].set_value(0xFF)
                return result
            retries += 1
        return ResponseStatus.FAILURE

    def off(self, group=0):
        """Turn off the switch."""
        asyncio.ensure_future(self.async_off())

    async def async_off(self, group=0):
        """Turn off the switch."""
        retries = 0
        while retries < 3:
            result = await self._off_cmd.async_send()
            if result == ResponseStatus.SUCCESS:
                self._groups[1].set_value(0x00)
                return result
            retries += 1
        return ResponseStatus.FAILURE

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._managers[ALL_LIGHTS_ON_OFF] = X10AllLightsOnOffManager(self._address)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()

        self._managers[ALL_LIGHTS_ON_OFF].subscribe(self._groups[1].set_value)
        self._managers[ALL_LIGHTS_ON_OFF].subscribe_on(
            self._events[1][ON_EVENT].trigger
        )
        self._managers[ALL_LIGHTS_ON_OFF].subscribe_off(
            self._events[1][OFF_EVENT].trigger
        )


class X10Dimmable(X10OnOff):
    """X10 Dimmable Switch."""

    def __init__(self, housecode, unitcode, steps: int = 22, max_level: int = 0xFF):
        """Init the X10Dimmable class."""
        super().__init__(housecode, unitcode)
        self._description = "X10 Dimmable Switch"
        self._steps = steps
        self._max_level = max_level
        self._increment = self._max_level / self._steps
        self._dim_cmd = X10CommandSend(self._address, X10Commands.DIM)
        self._bright_cmd = X10CommandSend(self._address, X10Commands.BRIGHT)

    @property
    def steps(self):
        """Return the number of steps from off to full on."""
        return self._steps

    # pylint: disable=arguments-renamed
    def on(self, on_level: int = 0xFF, group: int = 0):
        """Set the on level of the switch."""
        asyncio.ensure_future(self.async_on(on_level))

    # pylint: disable=arguments-renamed
    async def async_on(self, on_level: int = 0xFF, group: int = 0):
        """Set the on level of the switch."""
        if on_level == 0x00:
            return await self.async_off()
        if on_level == 0xFF:
            return await super().async_on()

        if on_level < 1:
            # Assume the user entered a precent on level
            on_level = on_level * self._max_level
        if self._groups[1].value is None:
            self._groups[1].set_value(0)
        change = on_level - self._groups[1].value
        steps = round(abs(change) / self._increment)
        method = self.async_bright if change > 0 else self.async_dim
        results = []
        for _ in range(0, steps):
            result = await method()
            results.append(result)
        return multiple_status(*results)

    def dim(self):
        """Dim the swich one step."""
        asyncio.ensure_future(self.async_dim)

    async def async_dim(self):
        """Dim the swich one step."""
        retries = 0
        while retries < 3:
            results = await self._dim_cmd.async_send()
            if results == ResponseStatus.SUCCESS:
                self._handle_dim_bright(-1)
                return results
            retries += 1
        return ResponseStatus.FAILURE

    def bright(self):
        """Dim the swich one step."""
        asyncio.ensure_future(self.async_bright)

    async def async_bright(self):
        """Dim the swich one step."""
        retries = 0
        while retries < 3:
            results = await self._bright_cmd.async_send()
            if results == ResponseStatus.SUCCESS:
                self._handle_dim_bright(1)
                return results
            retries += 1
        return ResponseStatus.FAILURE

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._managers[DIM_BRIGHT] = X10DimBrightenManager(self._address)

    def _register_groups(self):
        self._groups[1] = OnLevel(DIMMABLE_LIGHT, self._address, 1, 0)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._managers[DIM_BRIGHT].subscribe(self._handle_dim_bright)

    def _handle_dim_bright(self, on_level):
        """Handle a dim or bright command from the device."""
        new_value = self._groups[1].value + self._increment * on_level
        new_value = min(max(new_value, 0x00), 0xFF)
        self._groups[1].set_value(new_value)
