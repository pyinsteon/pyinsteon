"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from ..constants import FanSpeed
from ..events import (FAN_OFF_EVENT, FAN_OFF_FAST_EVENT, FAN_ON_EVENT,
                      FAN_ON_FAST_EVENT, Event)
from ..handlers.kpl.set_leds import SetLedsCommandHandler
from ..handlers.kpl.trigger_scene import TriggerSceneCommandHandler
from ..handlers.to_device.status_request import StatusRequestCommand
from ..states import DIMMABLE_FAN_STATE
from ..states.on_level import OnLevel
from .commands import (OFF_COMMAND, OFF_FAST_COMMAND, OFF_FAST_INBOUND,
                       OFF_INBOUND, ON_COMMAND, ON_FAST_COMMAND,
                       ON_FAST_INBOUND, ON_INBOUND, SET_LEDS_COMMAND,
                       STATUS_COMMAND, TRIGGER_SCENE_COMMAND)
from .variable_responder_base import VariableResponderBase


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


class DimmableLightingControl_FanLinc(DimmableLightingControl):
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
        self._events[FAN_ON_EVENT] = Event(
            name=FAN_ON_EVENT, address=self._address, group=2)

        self._events[FAN_OFF_EVENT] = Event(
            name=FAN_OFF_EVENT, address=self._address, group=2)

        self._events[FAN_ON_FAST_EVENT] = Event(
            name=FAN_ON_FAST_EVENT, address=self._address, group=2)

        self._events[FAN_OFF_FAST_EVENT] = Event(
            name=FAN_OFF_FAST_EVENT, address=self._address, group=2)

    def _register_operating_flags(self):
        from ..operating_flag import (
            PROGRAM_LOCK_ON, LED_BLINK_ON_TX_ON, RESUME_DIM_ON, LED_OFF,
            KEY_BEEP_ON, RF_DISABLE_ON, POWERLINE_DISABLE_ON, DATABASE_DELTA, CRC_ERROR_COUNT,
            SIGNAL_TO_NOISE_FAILURE_COUNT, X10_OFF, LED_BLINK_ON_ERROR_ON, CLEANUP_REPORT_ON)
        from ..extended_property import ON_LEVEL, X10_HOUSE, X10_UNIT, RAMP_RATE

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit4', 0)  # 10
        self._remove_operating_flag('bit5', 0)  # 20
        self._remove_operating_flag('bit6', 0)  # 40
        self._remove_operating_flag('bit7', 0)  # 80

        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0a, 0x0b)
        self._add_operating_flag(RF_DISABLE_ON, 0, 6, 0x0c, 0x0d)
        self._add_operating_flag(POWERLINE_DISABLE_ON, 0, 7, 0x0e, 0x0f)

        self._add_operating_flag(DATABASE_DELTA, 1, None, None, None)
        self._add_operating_flag(CRC_ERROR_COUNT, 2, None, None, None)
        self._add_operating_flag(SIGNAL_TO_NOISE_FAILURE_COUNT, 3, None, None, None)

        self._add_operating_flag(X10_OFF, 5, 1, 0x12, 0x13)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)
        self._add_operating_flag(CLEANUP_REPORT_ON, 5, 3, 0x16, 0x17)

        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)

    def _set_fan_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[2].value = status


class DimmableLightingControl_KeypadLinc(DimmableLightingControl):
    """KeypadLinc base class."""

    def __init__(self, button_list, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the GeneralController_MiniRemoteBase class."""
        from ..states.on_off import OnOff
        from ..states import ON_OFF_SWITCH_STATE
        super().__init__(address, cat, subcat, firmware, description, model, buttons=[1])
        for button in button_list:
            name = '{}_{}'.format(ON_OFF_SWITCH_STATE, button_list[button])
            self._states[button] = OnOff(name=name, address=self._address, group=button)
            self._add_button_handlers(button)

    async def async_on(self, on_level: int = 0xff, group: int = 0, fast: bool = False):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_on(on_level=on_level, group=group, fast=fast)
        kwargs = {}
        for curr_group in range(1, 9):
            var = 'group{}'.format(curr_group)
            kwargs[var] = True if curr_group == group else bool(self._states.get(curr_group))
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    async def async_off(self, group: int = 0, fast: bool = False):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_off(group=group, fast=fast)
        kwargs = {}
        for curr_group in range(1, 9):
            var = 'group{}'.format(curr_group)
            kwargs[var] = False if curr_group == group else bool(self._states.get(curr_group))
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    def _register_handlers(self):
        super()._register_handlers()
        self._handlers[SET_LEDS_COMMAND] = SetLedsCommandHandler(address=self.address)
        self._handlers[TRIGGER_SCENE_COMMAND] = TriggerSceneCommandHandler(address=self._address)

    def _add_button_handlers(self, button):
        self._handlers[SET_LEDS_COMMAND].subscribe(self._states[button])


class DimmableLightingControl_KeypadLinc_6(DimmableLightingControl_KeypadLinc):
    """KeypadLinc 6 button dimmer."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the DimmableLightingControl_KeypadLinc_6 class."""
        button_list = {3: 'A', 4: 'B', 5: 'C', 6: 'D'}
        super().__init__(button_list=button_list, address=address, cat=cat, subcat=subcat,
                         firmware=firmware, description=description, model=model)


class DimmableLightingControl_KeypadLinc_8(DimmableLightingControl_KeypadLinc):
    """KeypadLinc 8 button dimmer."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the DimmableLightingControl_KeypadLinc_6 class."""
        button_list = {2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
        super().__init__(button_list=button_list, address=address, cat=cat, subcat=subcat,
                         firmware=firmware, description=description, model=model)
