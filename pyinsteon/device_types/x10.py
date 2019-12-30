"""X10 devices."""
import asyncio

from .x10_base import X10DeviceBase
from ..states import ON_OFF_SWITCH
from ..managers.x10_manager import (
    X10OnOffManager,
    X10DimBrightenManager,
    X10AllLightsOnOffManager,
    X10AllUnitsOffManager,
)
from ..states.on_off import OnOff
from ..events import Event, ON_EVENT, OFF_EVENT
from ..handlers.to_device.x10_send import X10CommandSend
from ..constants import X10Commands, ResponseStatus
from ..utils import multiple_status

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

    def _register_states(self):
        self._states[1] = OnOff(ON_OFF_SWITCH, self._address, group=1)

    def _register_events(self):
        self._events[1] = {}
        self._events[1][ON_EVENT] = Event(ON_EVENT, self._address, group=1)
        self._events[1][OFF_EVENT] = Event(OFF_EVENT, self._address, group=1)

    def _subscribe_to_handelers_and_managers(self):
        self._managers[ON_OFF_SWITCH].subscribe(self._states[1].set_value)

        self._managers[ON_OFF_SWITCH].subscribe_on(self._events[1][ON_EVENT].trigger)
        self._managers[ON_OFF_SWITCH].subscribe_off(self._events[1][OFF_EVENT].trigger)


class X10OnOff(X10OnOffSensor):
    """X10 On/Off device."""

    def __init__(self, housecode, unitcode):
        """Init the X10OnOff class."""
        super().__init__(housecode, unitcode)
        self._description = "X10 On/Off Switch"

    def on(self):
        """Turn on the switch."""
        asyncio.ensure_future(self.async_on())

    async def async_on(self):
        """Turn on the switch."""
        cmd = X10CommandSend(self._address, X10Commands.ON)
        retries = 0
        while retries < 3:
            result = await cmd.async_send()
            if result == ResponseStatus.SUCCESS:
                self._states[1].set_value(0xFF)
                return result
            retries += 1
        return ResponseStatus.FAILURE

    def off(self):
        """Turn off the switch."""
        asyncio.ensure_future(self.async_on())

    async def async_off(self):
        """Turn off the switch."""
        cmd = X10CommandSend(self._address, X10Commands.OFF)
        retries = 0
        while retries < 3:
            result = await cmd.async_send()
            if result == ResponseStatus.SUCCESS:
                self._states[1].set_value(0x00)
                return result
            retries += 1
        return ResponseStatus.FAILURE

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._managers[ALL_LIGHTS_ON_OFF] = X10AllLightsOnOffManager(self._address)
        self._managers[ALL_UNITS_OFF] = X10AllUnitsOffManager(self._address)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()

        self._managers[ALL_LIGHTS_ON_OFF].subscribe(self._states[1].set_value)
        self._managers[ALL_UNITS_OFF].subscribe(self._states[1].set_value)
        self._managers[ALL_LIGHTS_ON_OFF].subscribe_on(
            self._events[1][ON_EVENT].trigger
        )
        self._managers[ALL_LIGHTS_ON_OFF].subscribe_off(
            self._events[1][OFF_EVENT].trigger
        )
        self._managers[ALL_UNITS_OFF].subscribe(self._events[1][OFF_EVENT].trigger)


class X10Dimmable(X10OnOff):
    """X10 Dimmable Switch."""

    def __init__(self, housecode, unitcode, steps: int = 22, max_level: int = 0xFF):
        """Init the X10Dimmable class."""
        super().__init__(housecode, unitcode)
        self._description = "X10 Dimmable Switch"
        self._steps = steps
        self._max_level = max_level

    @property
    def steps(self):
        """Return the number of steps from off to full on."""
        return self._steps

    # pylint: disable=arguments-differ
    def on(self, on_level: int):
        """Set the on level of the switch."""
        asyncio.ensure_future(self.async_on(on_level))

    # pylint: disable=arguments-differ
    async def async_on(self, on_level: int):
        """Set the on level of the switch."""
        if on_level == 0x00:
            return await self.async_off()
        if on_level == 0xFF:
            return await super().async_on()

        if on_level < 1:
            # Assume the user entered a precent on level
            on_level = on_level * self._max_level

        change = on_level - self._states[1].value
        increment = self._max_level / self._steps
        steps = round(abs(change) / increment)
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
        cmd = X10CommandSend(self._address, X10Commands.DIM)
        retries = 0
        while retries < 3:
            results = await cmd.async_send()
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
        cmd = X10CommandSend(self._address, X10Commands.BRIGHT)
        retries = 0
        while retries < 3:
            results = await cmd.async_send()
            if results == ResponseStatus.SUCCESS:
                self._handle_dim_bright(1)
                return results
            retries += 1
        return ResponseStatus.FAILURE

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._managers[DIM_BRIGHT] = X10DimBrightenManager(self._address)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._managers[DIM_BRIGHT].subscribe(self._handle_dim_bright)

    def _handle_dim_bright(self, on_level):
        """Handle a dim or bright command from the device."""
        new_value = self._states[1].value + self._steps * on_level
        new_value = min(max(new_value, 0x00), 0xFF)
        self._states[1].set_value(new_value)
