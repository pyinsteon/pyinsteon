"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from ..constants import FanSpeed
from ..handlers.to_device.set_leds import SetLedsCommandHandler
from ..handlers.to_device.status_request import StatusRequestCommand
from ..handlers.to_device.trigger_scene import TriggerSceneCommandHandler
from ..states import (DIMMABLE_FAN_STATE, DIMMABLE_LIGHT_STATE,
                      ON_OFF_SWITCH_STATE)
from ..states.on_off import OnOff
from .commands import (OFF_COMMAND, OFF_FAST_COMMAND, ON_COMMAND,
                       ON_FAST_COMMAND, SET_LEDS_COMMAND, STATUS_COMMAND_FAN,
                       TRIGGER_SCENE_COMMAND)
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
    def __init__(self, address, cat, subcat, firmware=0, description='', model=''):
        buttons = [1, 2]
        self._button_names = [DIMMABLE_LIGHT_STATE, DIMMABLE_FAN_STATE]
        super().__init__(address, cat, subcat, firmware=firmware, description=description,
                         model=model, buttons=buttons)

    def fan_on(self, on_level: FanSpeed = FanSpeed.HIGH, fast=False):
        """Turn on the fan.

        Parameters:
            on_level: Default FanSpeed.HIGH (full on). Set the fan on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        command_group = '{}_2'.format(command)
        fan_speed = int(on_level)
        # The send command converts to int
        self._handlers[command_group].send(on_level=fan_speed)

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
        command_group = '{}_2'.format(command)
        fan_speed = int(on_level)
        # The send command converts to int
        return await self._handlers[command_group].async_send(on_level=fan_speed)

    def fan_off(self, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.
        """
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        command_group = '{}_2'.format(command)
        self._handlers[command_group].send()

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
        command_group = '{}_2'.format(command)
        return await self._handlers[command_group].async_send(group=2)

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
        self._handlers[STATUS_COMMAND_FAN].send()

    async def async_fan_status(self):
        """Request the status of the fan.

        Returns a ResponseStatus value
            FAILURE: Device did not acknowledge the message
            SUCCESS: Device acknowledged the message
            UNCLEAR: Device received the message but did not confirm the action
        """
        return await self._handlers[STATUS_COMMAND_FAN].async_send()

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[STATUS_COMMAND_FAN] = StatusRequestCommand(self._address, 3)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[STATUS_COMMAND_FAN].subscribe(self._handle_fan_status)

    #pylint: disable=useless-super-delegation
    def _register_default_links(self):
        """Register default links."""
        super()._register_default_links()

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

    def _handle_fan_status(self, db_version, status):
        if int(status) == 0:
            self._states[2].set_value(FanSpeed.OFF)
        elif int(status) <= int(FanSpeed.LOW):
            self._states[2].set_value(FanSpeed.LOW)
        elif int(status) <= int(FanSpeed.MEDIUM):
            self._states[2].set_value(FanSpeed.MEDIUM)
        else:
            self._states[2].set_value(FanSpeed.HIGH)


# TODO setup operating flags for each KPL button
# TODO trigger scenes
class DimmableLightingControl_KeypadLinc(DimmableLightingControl):
    """KeypadLinc base class."""

    def __init__(self, button_list, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the GeneralController_MiniRemoteBase class."""
        self._button_list = button_list
        super().__init__(address, cat, subcat, firmware, description, model, buttons=[1])

    async def async_on(self, on_level: int = 0xff, group: int = 0, fast: bool = False):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_on(on_level=on_level, group=group, fast=fast)
        kwargs = self._change_led_status(led=group, on=True)
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    async def async_off(self, group: int = 0, fast: bool = False):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_off(group=group, fast=fast)
        kwargs = self._change_led_status(led=group, on=False)
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[SET_LEDS_COMMAND] = SetLedsCommandHandler(address=self.address)
        scene_group = '{}_{}'.format(TRIGGER_SCENE_COMMAND, 1)
        self._handlers[scene_group] = TriggerSceneCommandHandler(self._address, 1)
        for group in self._button_list:
            scene_group = '{}_{}'.format(TRIGGER_SCENE_COMMAND, group)
            self._handlers[scene_group] = TriggerSceneCommandHandler(self._address, group)

    def _register_states(self):
        super()._register_states()
        for button in self._button_list:
            name = '{}_{}'.format(ON_OFF_SWITCH_STATE, self._button_list[button])
            self._states[button] = OnOff(name=name, address=self._address, group=button)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        for button in self._button_list:
            self._handlers[SET_LEDS_COMMAND].subscribe(self._states[button].set_value)

    def _change_led_status(self, led, on):
        leds = {}
        for curr_led in range(1, 9):
            var = 'group{}'.format(curr_led)
            leds[var] = on if curr_led == led else bool(self._states.get(curr_led))
        return leds


class DimmableLightingControl_KeypadLinc_6(DimmableLightingControl_KeypadLinc):
    """KeypadLinc 6 button dimmer."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the DimmableLightingControl_KeypadLinc_6 class."""
        button_list = {3: 'a', 4: 'b', 5: 'c', 6: 'd'}
        super().__init__(button_list=button_list, address=address, cat=cat, subcat=subcat,
                         firmware=firmware, description=description, model=model)


class DimmableLightingControl_KeypadLinc_8(DimmableLightingControl_KeypadLinc):
    """KeypadLinc 8 button dimmer."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the DimmableLightingControl_KeypadLinc_6 class."""
        button_list = {2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'}
        super().__init__(button_list=button_list, address=address, cat=cat, subcat=subcat,
                         firmware=firmware, description=description, model=model)
