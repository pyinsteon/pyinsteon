"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from .variable_responder_base import VariableResponderBase
from ..handlers.to_device.status_request import StatusRequestCommand
from ..states import DIMMABLE_FAN_STATE
from ..states.on_level import OnLevel
from ..events import (Event, FAN_ON_EVENT, FAN_ON_FAST_EVENT, FAN_OFF_EVENT,
                      FAN_OFF_FAST_EVENT)
from ..constants import FanSpeed
from .commands import (ON_COMMAND, OFF_COMMAND, ON_FAST_COMMAND, OFF_FAST_COMMAND,
                       ON_INBOUND, OFF_INBOUND, ON_FAST_INBOUND, OFF_FAST_INBOUND,
                       STATUS_COMMAND)



class DimmableLightingControl(VariableResponderBase):
    """Dimmable Lighting Control Device."""


class DimmableLightingControl_LampLinc(DimmableLightingControl):
    """LampLinc based dimmable lights."""

    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_BLINK_ON_TX_ON, RESUME_DIM_ON,
                                      LED_ON, LOAD_SENSE_ON)
        from ..extended_property import (LED_DIMMING, ON_LEVEL, X10_HOUSE, X10_UNIT, RAMP_RATE)

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit2', 0)  # 04
        self._remove_operating_flag('bit4', 0)  # 10
        self._remove_operating_flag('bit5', 0)  # 20
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9)
        self._add_operating_flag(LOAD_SENSE_ON, 0, 5, 0x0a, 0x0b)

        self._add_property(LED_DIMMING, 3, 3)
        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)


class DimmableLightingControl_SwitchLinc(DimmableLightingControl):
    """SwichLinc based dimmable lights."""

    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_BLINK_ON_TX_ON, RESUME_DIM_ON,
                                      LED_ON, KEY_BEEP_ON, LED_BLINK_ON_ERROR_ON)
        from ..extended_property import (LED_DIMMING, ON_LEVEL, X10_HOUSE, X10_UNIT,
                                         RAMP_RATE)
        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit2', 0)  # 04
        self._remove_operating_flag('bit4', 0)  # 10
        self._remove_operating_flag('bit5', 0)  # 20
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0a, 0x0b)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)

        self._add_property(LED_DIMMING, 3, 3)
        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)


class DimmableLightingControl_InLineLinc(DimmableLightingControl_SwitchLinc):
    """InLineLinc based dimmable lights."""


class DimmableLightingControl_OutletLinc(DimmableLightingControl):
    """OutletLinc based dimmable lights."""

    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_BLINK_ON_TX_ON, LED_ON)
        from ..extended_property import (X10_HOUSE, X10_UNIT)

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit4', 0)  # 10
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9)

        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)


class DimmableLightingControl_DinRail(DimmableLightingControl):
    """DINRail based dimmable lights."""

    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_BLINK_ON_TX_ON, LED_ON, KEY_BEEP_ON)
        from ..extended_property import (LED_DIMMING, ON_LEVEL, X10_HOUSE, X10_UNIT,
                                         RAMP_RATE)

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit4', 0)  # 10
        self._remove_operating_flag('bit5', 0)  # 20
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0a, 0x0b)

        self._add_property(LED_DIMMING, 3, 3)
        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)


class DimmableLightingControl_2475F(DimmableLightingControl):
    """FanLinc model 2475F Dimmable Lighting Control.

    Device Class 0x01 subcat 0x2e
    """
    def fan_on(self, on_level: FanSpeed = FanSpeed.HIGH, fast=False):
        """Turn on the fan.

        Parameters:
            on_level: Default FanSpeed.HIGH (full on). Set the fan on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        # The send command converts to int
        self._handlers[command].send(on_level=on_level, group=2)

    async def async_fan_on(self, on_level: FanSpeed = FanSpeed.HIGH, fast=False):
        """Turn on the device.

        Parameters:
            on_level: Default FanSpeed.HIGH (full on). Set the fan on level.
            fast: Default False. If True, bypass fan ramp rate otherwise
            turn on at the ramp rate.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        # The send command converts to int
        return await self._handlers[command].async_send(on_level=on_level, group=2)

    def fan_off(self, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        self._handlers[command].send(group=2)

    async def async_fan_off(self, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        return await self._handlers[command].async_send(group=2)

    def status(self):
        """Request the status of the light and the fan."""
        super().status()
        self.fan_status()

    async def async_status(self):
        """Request the status fo the light and the fan."""
        from ..handlers import ResponseStatus
        light_status = await super().async_status()
        fan_status = await self.async_fan_status()
        if light_status == fan_status == ResponseStatus.SUCCESS:
            return ResponseStatus.SUCCESS
        if light_status == ResponseStatus.UNCLEAR or fan_status == ResponseStatus.UNCLEAR:
            return ResponseStatus.UNCLEAR
        return ResponseStatus.FAILURE

    def light_status(self):
        """Request the status of the light."""
        super().status()

    async def async_light_status(self):
        """Request the status of the light."""
        return await super().async_status()

    def fan_status(self):
        """Request the status of the fan."""
        self._handlers[STATUS_COMMAND].send(3)

    async def async_fan_status(self):
        """Request the status of the fan.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        await self._handlers[STATUS_COMMAND].async_send(3)

    #pylint: disable=useless-super-delegation
    def _register_default_links(self):
        """Register default links."""
        super()._register_default_links()

    def _register_handlers(self):
        super()._register_handlers()
        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address)

    def _register_states(self):
        super()._register_states()
        self._states[2] = OnLevel(name=DIMMABLE_FAN_STATE,
                                                   address=self._address,
                                                   group=2)
        state = self._states[2]
        state.add_handler(self._handlers[ON_COMMAND])
        state.add_handler(self._handlers[ON_INBOUND])
        state.add_handler(self._handlers[OFF_COMMAND])
        state.add_handler(self._handlers[OFF_INBOUND])
        state.add_handler(self._handlers[ON_FAST_COMMAND])
        state.add_handler(self._handlers[ON_FAST_INBOUND])
        state.add_handler(self._handlers[OFF_FAST_COMMAND])
        state.add_handler(self._handlers[OFF_FAST_INBOUND])

        self._handlers[STATUS_COMMAND].subscribe(self._set_fan_status)

    def _register_events(self):
        super()._register_events()
        self._events[FAN_ON_EVENT] = Event(name=FAN_ON_EVENT, address=self._address,
                                           group=2)
        self._events[FAN_OFF_EVENT] = Event(name=FAN_OFF_EVENT, address=self._address,
                                            group=2)
        self._events[FAN_ON_FAST_EVENT] = Event(name=FAN_ON_FAST_EVENT, address=self._address,
                                                group=2)
        self._events[FAN_OFF_FAST_EVENT] = Event(name=FAN_OFF_FAST_EVENT, address=self._address,
                                                 group=2)

    def _set_fan_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[2].value = status

#                                                         DimmableLightingControl_2334_222_6,
#                                                         DimmableLightingControl_2334_222_8)
