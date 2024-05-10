"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""

import asyncio
from collections.abc import Iterable
from functools import partial
from typing import Dict, Union

from ..config import (
    CLEANUP_REPORT_ON,
    CRC_ERROR_COUNT,
    DATABASE_DELTA,
    KEY_BEEP_ON,
    LED_BLINK_ON_ERROR_OFF,
    LED_BLINK_ON_ERROR_ON,
    LED_BLINK_ON_TX_ON,
    LED_DIMMING,
    LED_OFF,
    LOAD_BUTTON,
    LOAD_BUTTON_NUMBER,
    LOAD_SENSE_ON,
    NIGHT_MODE_ON,
    NO_CACHE,
    NON_TOGGLE_MASK,
    NON_TOGGLE_ON_OFF_MASK,
    OFF_MASK,
    ON_LEVEL,
    ON_MASK,
    POWERLINE_DISABLE_ON,
    PROGRAM_LOCK_ON,
    RADIO_BUTTON_GROUPS,
    RAMP_RATE,
    RAMP_RATE_IN_SEC,
    RED_LED_OFF,
    RELAY_AT_FULL_ON,
    RELAY_MODE_OFF,
    RESUME_DIM_ON,
    RF_DISABLE_ON,
    SIGNAL_TO_NOISE_FAILURE_COUNT,
    SKIP_SOME_HOPS,
    TOGGLE_BUTTON,
    TRIGGER_GROUP_MASK,
    X10_HOUSE,
    X10_OFF,
    X10_UNIT,
    YAKETY_YAK,
)
from ..config.extended_property import ExtendedProperty
from ..config.load_button import LoadButtonProperty
from ..config.radio_button import RadioButtonGroupsProperty
from ..config.ramp_rate import RampRateProperty
from ..config.toggle_button import ToggleButtonProperty
from ..constants import FanSpeed, PropertyType, ResponseStatus, ToggleMode
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT
from ..groups import (
    DIMMABLE_FAN,
    DIMMABLE_LIGHT,
    DIMMABLE_LIGHT_MAIN,
    DIMMABLE_OUTLET,
    ON_OFF_SWITCH_A,
    ON_OFF_SWITCH_B,
    ON_OFF_SWITCH_C,
    ON_OFF_SWITCH_D,
    ON_OFF_SWITCH_E,
    ON_OFF_SWITCH_F,
    ON_OFF_SWITCH_G,
    ON_OFF_SWITCH_H,
)
from ..groups.on_level import OnLevel
from ..groups.on_off import OnOff
from ..handlers.from_device.manual_change import ManualChangeInbound
from ..handlers.to_device.group_off import GroupOffCommand
from ..handlers.to_device.set_leds import SetLedsCommandHandler
from ..handlers.to_device.trigger_scene_off import TriggerSceneOffCommandHandler
from ..handlers.to_device.trigger_scene_on import TriggerSceneOnCommandHandler
from ..utils import bit_is_set, multiple_status, set_bit, set_fan_speed
from .device_commands import (
    MANUAL_CHANGE,
    OFF_COMMAND,
    OFF_FAST_COMMAND,
    ON_COMMAND,
    ON_FAST_COMMAND,
    SET_LEDS_COMMAND,
    STATUS_COMMAND,
)
from .i3_base import I3VariableResponderBase
from .variable_controller_base import ON_LEVEL_MANAGER
from .variable_responder_base import VariableResponderBase


class DimmableLightingControl(VariableResponderBase):
    """Dimmable Lighting Control Device."""

    def _register_handlers_and_managers(self):
        """Register command handlers and managers."""
        super()._register_handlers_and_managers()
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group][MANUAL_CHANGE] = ManualChangeInbound(
                    self._address, group
                )

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe methods to handlers and managers."""
        super()._subscribe_to_handelers_and_managers()
        self._managers[STATUS_COMMAND].remove_status_type(0)
        self._managers[STATUS_COMMAND].add_status_type(2, self._handle_status)
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group][MANUAL_CHANGE].subscribe(
                    self._async_on_manual_change
                )

    async def _async_on_manual_change(self, group=None):
        """Respond to a manual change of the device."""
        await self.async_status()


class DimmableLightingControl_LampLinc(DimmableLightingControl):
    """LampLinc based dimmable lights."""

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)
        self._add_operating_flag(LOAD_SENSE_ON, 0, 5, 0x0A, 0x0B)

        self._add_property(LED_DIMMING, 3, 3)
        self._add_property(X10_HOUSE, 5, None, prop_type=PropertyType.ADVANCED)
        self._add_property(X10_UNIT, 6, None, prop_type=PropertyType.ADVANCED)
        self._add_property(RAMP_RATE, 7, 5, prop_type=PropertyType.ADVANCED)
        self._add_property(ON_LEVEL, 8, 6)

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )


class DimmableLightingControl_SwitchLincBase(DimmableLightingControl):
    """SwichLinc based dimmable lights."""

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)

        self._add_property(X10_HOUSE, 5, None, prop_type=PropertyType.ADVANCED)
        self._add_property(X10_UNIT, 6, None, prop_type=PropertyType.ADVANCED)
        self._add_property(RAMP_RATE, 7, 5, prop_type=PropertyType.ADVANCED)
        self._add_property(ON_LEVEL, 8, 6)

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )


class DimmableLightingControl_SwitchLinc01(DimmableLightingControl_SwitchLincBase):
    """SwichLinc based dimmable lights.

    Uses command 0x2E 0x00 0x00 0x03 for LED dimming.
    """

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        if (self._subcat == 0x04 and self._firmware >= 0x30) or (
            self._subcat == 0x19 and self._firmware >= 0x41
        ):
            self._add_property(LED_DIMMING, 9, 7)
        else:
            self._add_property(LED_DIMMING, 3, 3)


class DimmableLightingControl_SwitchLinc02(DimmableLightingControl_SwitchLincBase):
    """SwichLinc based dimmable lights.

    Uses command 0x2E 0x00 0x00 0x07 for LED dimming.
    """

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_property(LED_DIMMING, 9, 7)


class DimmableLightingControl_ToggleLinc(DimmableLightingControl_SwitchLinc01):
    """SwichLinc based dimmable lights."""


class DimmableLightingControl_InLineLinc01(DimmableLightingControl_SwitchLinc01):
    """InLineLinc based dimmable lights.

    Uses command 0x2E 0x00 0x00 0x03 for LED dimming.
    """


class DimmableLightingControl_InLineLinc02(DimmableLightingControl_SwitchLinc02):
    """InLineLinc based dimmable lights.

    Uses command 0x2E 0x00 0x00 0x07 for LED dimming.
    """


class DimmableLightingControl_OutletLinc(DimmableLightingControl):
    """OutletLinc based dimmable lights."""

    def __init__(self, address, cat, subcat, firmware=0, description="", model=""):
        """Init the DimmableLightingControl_OutletLinc class."""
        buttons = {1: (DIMMABLE_OUTLET, 0)}
        super().__init__(
            address,
            cat,
            subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
        )

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)

        self._add_property(X10_HOUSE, 5, None, prop_type=PropertyType.ADVANCED)
        self._add_property(X10_UNIT, 6, None, prop_type=PropertyType.ADVANCED)


class DimmableLightingControl_DinRail(DimmableLightingControl):
    """DINRail based dimmable lights."""

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)

        self._add_property(X10_HOUSE, 5, None, prop_type=PropertyType.ADVANCED)
        self._add_property(X10_UNIT, 6, None, prop_type=PropertyType.ADVANCED)
        self._add_property(RAMP_RATE, 7, 5, prop_type=PropertyType.ADVANCED)
        self._add_property(ON_LEVEL, 8, 6)
        self._add_property(LED_DIMMING, 9, 7)

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )


class DimmableLightingControl_FanLinc(DimmableLightingControl):
    """FanLinc model 2475F Dimmable Lighting Control.

    Device Class 0x01 subcat 0x2e

    """

    def __init__(self, address, cat, subcat, firmware=0, description="", model=""):
        """Init the DimmableLightingControl_FanLinc class."""
        buttons = {1: (DIMMABLE_LIGHT, 0), 2: (DIMMABLE_FAN, 3)}
        super().__init__(
            address,
            cat,
            subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
        )

    def fan_on(self, on_level: FanSpeed = FanSpeed.HIGH, fast=False):
        """Turn on the fan.

        Parameters:
            on_level: Default FanSpeed.HIGH (full on). Set the fan on level.
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.

        """
        group = 2
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        self._handlers[group][command].send(on_level=int(set_fan_speed(on_level)))

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
        group = 2
        command = ON_FAST_COMMAND if fast else ON_COMMAND
        return await self._handlers[group][command].async_send(
            on_level=int(set_fan_speed(on_level))
        )

    def fan_off(self, fast=False):
        """Turn off the device.

        Parameters:
            fast: Default False. If True, bypass device ramp rate otherwise
            turn on at the ramp rate.

        """
        group = 2
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        self._handlers[group][command].send()

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
        group = 2
        command = OFF_FAST_COMMAND if fast else OFF_COMMAND
        return await self._handlers[group][command].async_send()

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._managers[STATUS_COMMAND].add_status_type(3, self._handle_fan_status)

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()

        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(RF_DISABLE_ON, 0, 6, 0x0C, 0x0D)
        self._add_operating_flag(POWERLINE_DISABLE_ON, 0, 7, 0x0E, 0x0F)

        self._add_operating_flag(DATABASE_DELTA, 1, None, None, None)
        self._add_operating_flag(CRC_ERROR_COUNT, 2, None, None, None)
        self._add_operating_flag(SIGNAL_TO_NOISE_FAILURE_COUNT, 3, None, None, None)

        self._add_operating_flag(X10_OFF, 5, 1, 0x12, 0x13)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)
        self._add_operating_flag(CLEANUP_REPORT_ON, 5, 3, 0x16, 0x17)

        self._add_property(X10_HOUSE, 5, None, prop_type=PropertyType.ADVANCED)
        self._add_property(X10_UNIT, 6, None, prop_type=PropertyType.ADVANCED)
        self._add_property(RAMP_RATE, 7, 5, prop_type=PropertyType.ADVANCED)
        self._add_property(ON_LEVEL, 8, 6)

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )

    def _handle_fan_status(self, db_version, status):
        self._groups[2].set_value(status)


class DimmableLightingControl_KeypadLinc(DimmableLightingControl):
    """KeypadLinc base class."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
    ):
        """Init the GeneralController_MiniRemoteBase class."""
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )
        self._on_off_lock = asyncio.Lock()

    async def async_on(self, on_level: int = 0xFF, group: int = 0, fast: bool = False):
        """Turn on the button LED."""
        if group in [0, 1]:
            result = await super().async_on(on_level=on_level, group=group, fast=fast)
        else:
            async with self._on_off_lock:
                kwargs = self._calc_led_status(led=group, is_on=True)
                result = await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)
        if result == ResponseStatus.SUCCESS:
            event = ON_FAST_EVENT if fast else ON_EVENT
            self._update_led_state(group=group, value=on_level, event=event)
        elif result == ResponseStatus.DIRECT_NAK_PRE_NAK:
            await self.async_status()
        return result

    async def async_off(self, group: int = 0, fast: bool = False):
        """Turn off the button LED."""
        if group in [0, 1]:
            result = await super().async_off(group=group, fast=fast)
        else:
            async with self._on_off_lock:
                kwargs = self._calc_led_status(led=group, is_on=False)
                result = await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)
        if result == ResponseStatus.SUCCESS:
            event = OFF_FAST_EVENT if fast else OFF_EVENT
            self._update_led_state(group=group, value=0, event=event)
        elif result == ResponseStatus.DIRECT_NAK_PRE_NAK:
            await self.async_status()
        return result

    async def async_trigger_scene_on(
        self, group: int, on_level: int = 255, fast: bool = False
    ):
        """Trigger an All-Link group on."""
        cmd = TriggerSceneOnCommandHandler(self._address, group)
        return await cmd.async_send(on_level, fast)

    async def async_trigger_scene_off(self, group: int, fast: bool = False):
        """Trigger an All-Link group off."""
        cmd = TriggerSceneOffCommandHandler(self._address, group)
        return await cmd.async_send(fast)

    def set_radio_buttons(self, buttons: Iterable):
        """Set a group of buttons to act as radio buttons.

        This takes in a iterable set of buttons (eg. (3,4,5,6)) to act as radio buttons where
        no two buttons are on at the same time.
        """
        if len(buttons) < 2:
            raise IndexError("At least two buttons required.")

        for button in buttons:
            if button not in self._buttons.keys():
                raise ValueError(f"Button {button} not in button list.")
            button_str = f"_{button}" if button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            if not on_mask.is_loaded or not off_mask.is_loaded:
                on_mask.set_value(0)
                off_mask.set_value(0)
            on_mask_new_value = 0
            off_mask_new_value = 0
            for bit in range(0, 8):
                if bit + 1 in buttons:
                    on_mask_value = bit != button - 1
                    off_mask_value = bit != button - 1
                else:
                    on_mask_value = bit_is_set(on_mask.value, bit)
                    off_mask_value = bit_is_set(off_mask.value, bit)
                on_mask_new_value = set_bit(on_mask_new_value, bit, on_mask_value)
                off_mask_new_value = set_bit(off_mask_new_value, bit, off_mask_value)
            on_mask.new_value = on_mask_new_value
            off_mask.new_value = off_mask_new_value

    def clear_radio_buttons(self, buttons: Iterable):
        """Clear the radio button behavior of the button.

        This takes in a single button number or a collection of buttons.
        For any button received, the radio button behavior of that button and
        any button that is grouped with that button will be cleared.

        Example:
            - Buttons C and D are currently radio buttons
            - Call `clear_radio_buttons(3)` which represents the C button.
            - Because C and D are currently grouped as radio buttons,
              both C and D will have their on and off masks changed to clear the
              link to the other button.

        """
        other_buttons = [
            button for button in self._buttons if button not in buttons and button != 1
        ]
        addl_buttons = []
        for other_button in other_buttons:
            button_str = f"_{other_button}" if other_button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            if not on_mask.is_loaded or not off_mask.is_loaded:
                on_mask.set_value(0)
                off_mask.set_value(0)
            for button in buttons:
                bit = button - 1
                on_set = (
                    bit_is_set(on_mask.new_value, bit)
                    if on_mask.is_dirty
                    else bit_is_set(on_mask.value, bit)
                )
                off_set = (
                    bit_is_set(off_mask.new_value, bit)
                    if off_mask.is_dirty
                    else bit_is_set(off_mask.value, bit)
                )
                if on_set or off_set and other_button not in addl_buttons:
                    addl_buttons.append(other_button)
                    continue

        for button in buttons:
            button_str = f"_{button}" if button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            on_mask.new_value = 0
            off_mask.new_value = 0

        for addl_button in addl_buttons:
            button_str = f"_{addl_button}" if addl_button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            if not on_mask.is_loaded or not off_mask.is_loaded:
                on_mask.set_value(0)
                off_mask.set_value(0)
            for button in buttons:
                if on_mask.is_dirty:
                    on_mask.new_value = set_bit(on_mask.new_value, button - 1, False)
                else:
                    on_mask.new_value = set_bit(on_mask.value, button - 1, False)
                if off_mask.is_dirty:
                    off_mask.new_value = set_bit(off_mask.new_value, button - 1, False)
                else:
                    off_mask.new_value = set_bit(off_mask.value, button - 1, False)

    def set_toggle_mode(self, button: int, toggle_mode: ToggleMode):
        """Set the toggle mode of a button.

        Usage:
            button: Integer of the button number
            toggle_mode: Integer of the toggle mode
                0: Toggle
                1: Non-Toggle ON only
                2: Non-Toggle OFF only
        """
        if button not in self._buttons.keys():
            raise ValueError(f"Button {button} not in button list.")
        try:
            toggle_mode = ToggleMode(toggle_mode)
        except ValueError as err:
            raise ValueError(
                f"Toggle mode {toggle_mode} invalid. Valid modes are [0, 1, 2]"
            ) from err

        toggle_mask = self.properties[NON_TOGGLE_MASK]
        on_off_mask = self.properties[NON_TOGGLE_ON_OFF_MASK]
        if not toggle_mask.is_loaded or not on_off_mask.is_loaded:
            toggle_mask.set_value(0)
            on_off_mask.set_value(0)

        if toggle_mask.new_value is None:
            toggle_mask_test = toggle_mask.value
        else:
            toggle_mask_test = toggle_mask.new_value

        if on_off_mask.new_value is None:
            on_off_mask_test = on_off_mask.value
        else:
            on_off_mask_test = on_off_mask.new_value

        if toggle_mode == ToggleMode.TOGGLE:
            toggle_mask.new_value = set_bit(toggle_mask_test, button - 1, False)
            on_off_mask.new_value = set_bit(on_off_mask_test, button - 1, False)
        elif toggle_mode == ToggleMode.ON_ONLY:
            toggle_mask.new_value = set_bit(toggle_mask_test, button - 1, True)
            on_off_mask.new_value = set_bit(on_off_mask_test, button - 1, True)
        else:
            toggle_mask.new_value = set_bit(toggle_mask_test, button - 1, True)
            on_off_mask.new_value = set_bit(on_off_mask_test, button - 1, False)

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[SET_LEDS_COMMAND] = SetLedsCommandHandler(address=self.address)

    def _register_groups(self):
        for button in self._buttons:
            name = self._buttons[button][0]
            status_type = self._buttons[button][1]
            if button == 1:
                self._groups[button] = OnLevel(
                    name=name,
                    address=self._address,
                    group=button,
                    status_type=status_type,
                )
            else:
                self._groups[button] = OnOff(
                    name=name,
                    address=self._address,
                    group=button,
                    status_type=status_type,
                )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._managers[STATUS_COMMAND].add_status_type(1, self._led_status)
        for group in self._buttons:
            if group != 1:
                led_method = partial(self._async_led_follow_check, group=group)
                self._managers[group][ON_LEVEL_MANAGER].subscribe(led_method)

    def _async_led_follow_check(self, group, on_level):
        """Check the other LEDs to confirm if they follow the effected LED."""
        for button in self._buttons:
            if button == group:
                continue
            button_str = f"_{button}" if button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            if not on_mask.is_loaded or not off_mask.is_loaded:
                continue
            follow = bit_is_set(on_mask.value, group)
            set_off = bit_is_set(off_mask.value, group)
            if follow:
                if set_off:
                    self._groups[button].value = 0
                else:
                    self._groups[button].value = on_level

    def _calc_led_status(self, led, is_on):
        leds = {}
        for curr_led in range(1, 9):
            var = f"group{curr_led}"
            curr_group = self._groups.get(curr_led)
            curr_val = bool(curr_group.value) if curr_group else False
            leds[var] = is_on if curr_led == led else curr_val
        return leds

    def _update_led_state(self, group, value, event):
        """Check if the LED is toggle or not and set value."""
        if not self._groups.get(group):
            return
        if self._properties[NON_TOGGLE_MASK].value is not None:
            non_toogle = bit_is_set(self._properties[NON_TOGGLE_MASK].value, group)
        else:
            non_toogle = False
        if non_toogle:
            self._groups[group].value = 0
        else:
            self._groups[group].value = value
        self._events[group][event].trigger(value)

    def _led_status(self, db_version, status):
        """Set the on level of the LED from a status command."""
        for bit in range(2, 9):
            state = self._groups.get(bit)
            if state:
                state.value = bit_is_set(status, bit - 1)

    def _register_op_flags_and_props(self):
        """Register operating flags."""
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(RF_DISABLE_ON, 0, 6, 0x0C, 0x0D)
        self._add_operating_flag(POWERLINE_DISABLE_ON, 0, 7, 0x0E, 0x0F)
        self._add_operating_flag(LED_BLINK_ON_ERROR_OFF, 5, 2, 0x14, 0x15)

        self._add_property(LED_DIMMING, 9, 7, 1)
        self._add_property(NON_TOGGLE_MASK, 0x0A, 0x08, prop_type=PropertyType.ADVANCED)
        self._add_property(
            NON_TOGGLE_ON_OFF_MASK, 0x0D, 0x0B, prop_type=PropertyType.ADVANCED
        )
        self._add_property(
            TRIGGER_GROUP_MASK, 0x0E, 0x0C, prop_type=PropertyType.ADVANCED
        )
        for button in self._buttons:
            button_str = f"_{button}" if button != 1 else ""
            self._add_property(
                f"{ON_MASK}{button_str}", 3, 2, button, prop_type=PropertyType.ADVANCED
            )
            self._add_property(
                f"{OFF_MASK}{button_str}", 4, 3, button, prop_type=PropertyType.ADVANCED
            )
            self._add_property(
                f"{X10_HOUSE}{button_str}",
                5,
                None,
                button,
                prop_type=PropertyType.ADVANCED,
            )
            self._add_property(
                f"{X10_UNIT}{button_str}",
                6,
                None,
                button,
                prop_type=PropertyType.ADVANCED,
            )
            self._add_property(
                f"{RAMP_RATE}{button_str}",
                7,
                5,
                button,
                prop_type=PropertyType.ADVANCED,
            )
            self._add_property(
                f"{ON_LEVEL}{button_str}", 8, 6, button, prop_type=PropertyType.ADVANCED
            )

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )
        self._config[RADIO_BUTTON_GROUPS] = RadioButtonGroupsProperty(
            self, RADIO_BUTTON_GROUPS
        )
        for group in self._groups:
            if group == 1:
                continue
            button = self._buttons[group][0]
            name = f"{TOGGLE_BUTTON}_{button[-1]}"
            self._config[name] = ToggleButtonProperty(
                self._address,
                name,
                group,
                self.properties[NON_TOGGLE_MASK],
                self.properties[NON_TOGGLE_ON_OFF_MASK],
            )


class DimmableLightingControl_KeypadLinc_6(DimmableLightingControl_KeypadLinc):
    """KeypadLinc 6 button dimmer."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the DimmableLightingControl_KeypadLinc_6 class."""
        buttons = {
            1: (DIMMABLE_LIGHT_MAIN, 0),
            3: (ON_OFF_SWITCH_A, 1),
            4: (ON_OFF_SWITCH_B, 1),
            5: (ON_OFF_SWITCH_C, 1),
            6: (ON_OFF_SWITCH_D, 1),
        }
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
        )


class DimmableLightingControl_KeypadLinc_8(DimmableLightingControl_KeypadLinc):
    """KeypadLinc 8 button dimmer."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the DimmableLightingControl_KeypadLinc_6 class."""
        buttons = {
            1: (DIMMABLE_LIGHT_MAIN, 0),
            2: (ON_OFF_SWITCH_B, 1),
            3: (ON_OFF_SWITCH_C, 1),
            4: (ON_OFF_SWITCH_D, 1),
            5: (ON_OFF_SWITCH_E, 1),
            6: (ON_OFF_SWITCH_F, 1),
            7: (ON_OFF_SWITCH_G, 1),
            8: (ON_OFF_SWITCH_H, 1),
        }
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
        )


class DimmableLightingControl_Dial(I3VariableResponderBase):
    """Dimmable i3 Dial."""

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe methods to handlers and managers."""
        super()._subscribe_to_handelers_and_managers()
        self._managers[STATUS_COMMAND].remove_status_type(0)
        self._managers[STATUS_COMMAND].add_status_type(2, self._handle_status)
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group][MANUAL_CHANGE].subscribe(
                    self._async_on_manual_change
                )

    async def _async_on_manual_change(self, group=None):
        """Respond to a manual change of the device."""
        await self.async_status()

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )


class DimmableLightingControl_I3_KeypadLinc_4(I3VariableResponderBase):
    """I3 dimmable 4 button KeypadLink device."""

    _is_kpl = True
    _op_flags_data_4 = {
        0: YAKETY_YAK,
        1: RED_LED_OFF,
        2: SKIP_SOME_HOPS,
        3: RELAY_AT_FULL_ON,
        4: f"{NIGHT_MODE_ON}_kpl",
        5: f"{NO_CACHE}_kpl",
    }

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the DimmableLightingControl_I3_KeypadLink_4 class."""
        buttons = {
            1: (ON_OFF_SWITCH_A, 1),
            2: (ON_OFF_SWITCH_B, 1),
            3: (ON_OFF_SWITCH_C, 1),
            4: (ON_OFF_SWITCH_D, 1),
        }
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
        )
        self._on_off_lock = asyncio.Lock()

    @property
    def load_button(self):
        """Return the button that controls the load."""
        load_button = self._properties[LOAD_BUTTON_NUMBER].value
        load_button = 1 if load_button in [0, None] else load_button
        return load_button

    async def async_on(self, on_level: int = 0xFF, group: int = 0, fast: bool = False):
        """Turn on the button LED."""
        group = self.load_button if not group else group
        led_kwargs = {}
        event = ON_FAST_EVENT if fast else ON_EVENT
        result_load = ResponseStatus.SUCCESS
        result_led = ResponseStatus.SUCCESS
        if group != self.load_button:
            load_new_state = self._get_led_follow_state(
                button1=group, button2=self.load_button, new_state=on_level
            )
            if load_new_state != bool(self._groups[self.load_button].value):
                if load_new_state:
                    result_load = await super().async_on(fast=fast)
                else:
                    result_load = await super().async_off(fast=fast)
        if group == self.load_button:
            result_load = await super().async_on(
                on_level=on_level, group=group, fast=fast
            )
        if group != self.load_button or self._has_follow_leds(group):
            async with self._on_off_lock:
                led_kwargs = self._calc_set_leds_command_kwargs(
                    led=group, is_on=bool(on_level)
                )
                result_led = await self._handlers[SET_LEDS_COMMAND].async_send(
                    **led_kwargs
                )

        result = multiple_status(result_load, result_led)
        if result == ResponseStatus.SUCCESS:
            await self._async_update_led_state(
                group=group, value=on_level, event=event, led_kwargs=led_kwargs
            )
        else:
            await self.async_status()
        return result

    async def async_off(self, group: int = 0, fast: bool = False):
        """Turn off the button LED."""
        group = self.load_button if not group else group
        led_kwargs = {}
        event = OFF_FAST_EVENT if fast else OFF_EVENT
        result_load = ResponseStatus.SUCCESS
        result_led = ResponseStatus.SUCCESS
        if group == self.load_button:
            result_load = await super().async_off(group=group, fast=fast)
        if group != self.load_button or self._has_follow_leds(group):
            async with self._on_off_lock:
                led_kwargs = self._calc_set_leds_command_kwargs(led=group, is_on=False)
                result_led = await self._handlers[SET_LEDS_COMMAND].async_send(
                    **led_kwargs
                )

        result = multiple_status(result_load, result_led)
        if result == ResponseStatus.SUCCESS:
            await self._async_update_led_state(
                group=group, value=0, event=event, led_kwargs=led_kwargs
            )
        else:
            await self.async_status()
        return result

    async def async_trigger_scene_on(
        self, group: int, on_level: int = 255, fast: bool = False
    ):
        """Trigger an All-Link group on."""
        cmd = TriggerSceneOnCommandHandler(self._address, group)
        return await cmd.async_send(on_level, fast)

    async def async_trigger_scene_off(self, group: int, fast: bool = False):
        """Trigger an All-Link group off."""
        cmd = TriggerSceneOffCommandHandler(self._address, group)
        return await cmd.async_send(fast)

    async def async_group_off(self, group: int) -> ResponseStatus:
        """Trigger a group off."""
        cmd = GroupOffCommand(address=self._address)
        return await cmd.async_send(group=group)

    def set_radio_buttons(self, buttons: Iterable):
        """Set a group of buttons to act as radio buttons.

        This takes in a iterable set of buttons (eg. (3,4,5,6)) to act as radio buttons where
        no two buttons are on at the same time.
        """
        if len(buttons) < 2:
            raise IndexError("At least two buttons required.")

        for button in buttons:
            if button not in self._buttons.keys():
                raise ValueError(f"Button {button} not in button list.")
            button_str = f"_{button}" if button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            if not on_mask.is_loaded or not off_mask.is_loaded:
                on_mask.set_value(0)
                off_mask.set_value(0)
            on_mask_new_value = 0
            off_mask_new_value = 0
            for bit in range(0, 8):
                if bit + 1 in buttons:
                    on_mask_value = bit != button - 1
                    off_mask_value = bit != button - 1
                else:
                    on_mask_value = bit_is_set(on_mask.value, bit)
                    off_mask_value = bit_is_set(off_mask.value, bit)
                on_mask_new_value = set_bit(on_mask_new_value, bit, on_mask_value)
                off_mask_new_value = set_bit(off_mask_new_value, bit, off_mask_value)
            on_mask.new_value = on_mask_new_value
            off_mask.new_value = off_mask_new_value

    def clear_radio_buttons(self, buttons: Iterable):
        """Clear the radio button behavior of the button.

        This takes in a single button number or a collection of buttons.
        For any button received, the radio button behavior of that button and
        any button that is grouped with that button will be cleared.

        Example:
            - Buttons C and D are currently radio buttons
            - Call `clear_radio_buttons(3)` which represents the C button.
            - Because C and D are currently grouped as radio buttons,
              both C and D will have their on and off masks changed to clear the
              link to the other button.

        """
        other_buttons = [
            button for button in self._buttons if button not in buttons and button != 1
        ]
        addl_buttons = []
        for other_button in other_buttons:
            button_str = f"_{other_button}" if other_button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            if not on_mask.is_loaded or not off_mask.is_loaded:
                on_mask.set_value(0)
                off_mask.set_value(0)
            for button in buttons:
                bit = button - 1
                on_set = (
                    bit_is_set(on_mask.new_value, bit)
                    if on_mask.is_dirty
                    else bit_is_set(on_mask.value, bit)
                )
                off_set = (
                    bit_is_set(off_mask.new_value, bit)
                    if off_mask.is_dirty
                    else bit_is_set(off_mask.value, bit)
                )
                if on_set or off_set and other_button not in addl_buttons:
                    addl_buttons.append(other_button)
                    continue

        for button in buttons:
            button_str = f"_{button}" if button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            on_mask.new_value = 0
            off_mask.new_value = 0

        for addl_button in addl_buttons:
            button_str = f"_{addl_button}" if addl_button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            if not on_mask.is_loaded or not off_mask.is_loaded:
                on_mask.set_value(0)
                off_mask.set_value(0)
            for button in buttons:
                if on_mask.is_dirty:
                    on_mask.new_value = set_bit(on_mask.new_value, button - 1, False)
                else:
                    on_mask.new_value = set_bit(on_mask.value, button - 1, False)
                if off_mask.is_dirty:
                    off_mask.new_value = set_bit(off_mask.new_value, button - 1, False)
                else:
                    off_mask.new_value = set_bit(off_mask.value, button - 1, False)

    def set_toggle_mode(self, button: int, toggle_mode: ToggleMode):
        """Set the toggle mode of a button.

        Usage:
            button: Integer of the button number
            toggle_mode: Integer of the toggle mode
                0: Toggle
                1: Non-Toggle ON only
                2: Non-Toggle OFF only
        """
        if button not in self._buttons.keys():
            raise ValueError(f"Button {button} not in button list.")
        try:
            toggle_mode = ToggleMode(toggle_mode)
        except ValueError as err:
            raise ValueError(
                f"Toggle mode {toggle_mode} invalid. Valid modes are [0, 1, 2]"
            ) from err

        toggle_mask = self.properties[NON_TOGGLE_MASK]
        on_off_mask = self.properties[NON_TOGGLE_ON_OFF_MASK]
        if not toggle_mask.is_loaded or not on_off_mask.is_loaded:
            toggle_mask.set_value(0)
            on_off_mask.set_value(0)

        if toggle_mask.new_value is None:
            toggle_mask_test = toggle_mask.value
        else:
            toggle_mask_test = toggle_mask.new_value

        if on_off_mask.new_value is None:
            on_off_mask_test = on_off_mask.value
        else:
            on_off_mask_test = on_off_mask.new_value

        if toggle_mode == ToggleMode.TOGGLE:
            toggle_mask.new_value = set_bit(toggle_mask_test, button - 1, False)
            on_off_mask.new_value = set_bit(on_off_mask_test, button - 1, False)
        elif toggle_mode == ToggleMode.ON_ONLY:
            toggle_mask.new_value = set_bit(toggle_mask_test, button - 1, True)
            on_off_mask.new_value = set_bit(on_off_mask_test, button - 1, True)
        else:
            toggle_mask.new_value = set_bit(toggle_mask_test, button - 1, True)
            on_off_mask.new_value = set_bit(on_off_mask_test, button - 1, False)

    def _register_groups(self):
        """Register the groups."""
        super()._register_groups()
        for group, state in self._groups.items():
            if group != 1:
                state.is_dimmable = False

    def _register_op_flags_and_props(self):
        """Register operating flags and properties.

        Not running the Super method since the i3 properties are sufficiently different than the legacy properties.
        """
        self._register_default_op_flags_and_props(dimmable=True, additional_flags=[])

        self._add_operating_flag(
            TRIGGER_GROUP_MASK, 8, None, None, None, False, PropertyType.ADVANCED
        )
        self._operating_flags[TRIGGER_GROUP_MASK].is_read_only = False
        self._properties[LOAD_BUTTON_NUMBER] = ExtendedProperty(
            address=self._address,
            name=LOAD_BUTTON_NUMBER,
            value_type=int,
            is_reversed=False,
            is_read_only=False,
            prop_type=PropertyType.ADVANCED,
        )
        self._properties[LOAD_BUTTON_NUMBER].set_value(1)
        self._add_ext_prop_read_manager({})
        self._add_ext_prop_write_manager(
            properties={3: self._properties[LOAD_BUTTON_NUMBER]}, data2=0x13
        )

    def _register_config(self):
        """Register configuration items."""
        super()._register_config()
        self._config[RAMP_RATE_IN_SEC] = RampRateProperty(
            self._address, RAMP_RATE_IN_SEC, self._properties[RAMP_RATE]
        )
        self._config[RADIO_BUTTON_GROUPS] = RadioButtonGroupsProperty(
            self, RADIO_BUTTON_GROUPS
        )
        for group in self._groups:
            if group == 1:
                continue
            button = self._buttons[group][0]
            name = f"{TOGGLE_BUTTON}_{button[-1]}"
            self._config[name] = ToggleButtonProperty(
                self._address,
                name,
                group,
                self.properties[NON_TOGGLE_MASK],
                self.properties[NON_TOGGLE_ON_OFF_MASK],
            )
        self._config[LOAD_BUTTON] = LoadButtonProperty(
            self._address,
            LOAD_BUTTON,
            self._properties[LOAD_BUTTON_NUMBER],
            list(self._groups),
        )

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[SET_LEDS_COMMAND] = SetLedsCommandHandler(address=self.address)
        self._add_ext_prop_write_manager(
            {3: self._operating_flags[TRIGGER_GROUP_MASK]}, 0x0C, 0x00, 0x00
        )

    def _subscribe_to_handelers_and_managers(self):
        # Not running super due to the LOAD_BUTTON_NUMBER config property
        super()._subscribe_to_handelers_and_managers()
        self._managers[STATUS_COMMAND].add_status_type(1, self._async_handle_led_status)
        for group in self._buttons:
            led_method = partial(self._async_led_follow_check, group=group)
            self._managers[group][ON_LEVEL_MANAGER].subscribe(
                led_method,
            )
        self._properties[LOAD_BUTTON_NUMBER].subscribe(
            self._handle_load_button_property__changed
        )

    def _handle_status(self, db_version, status):
        """Handle the status response."""
        # Need to check which button is the load button
        load = self.load_button
        relay_mode = self._operating_flags[RELAY_MODE_OFF].value
        relay_mode = False if relay_mode is None else relay_mode
        self._groups[load].is_dimmable = not relay_mode
        self._groups[load].set_value(status)

    async def _async_handle_led_status(self, db_version, status):
        """Set the on level of the LED from a status command."""
        load_button = self._properties[LOAD_BUTTON_NUMBER].value
        load_button = 1 if load_button in [0, None] else load_button
        for bit in range(1, 9):
            state = self._groups.get(bit)
            if state:
                value = bit_is_set(status, bit - 1)
                if bit == self.load_button and bool(state.value) != value:
                    await self.async_status()
                else:
                    state.is_dimmable = False
                    state.value = value

    def _get_led_follow_state(self, button1, button2, new_state) -> bool:
        """Return the state of button2 based on new_state of button1."""
        if button1 == button2:
            return new_state
        button2_str = f"_{button2}" if button2 != 1 else ""
        on_mask = self._properties[f"{ON_MASK}{button2_str}"]
        off_mask = self._properties[f"{OFF_MASK}{button2_str}"]
        if not on_mask.is_loaded or not off_mask.is_loaded:
            return False
        follow = bit_is_set(on_mask.value, button1 - 1)
        set_off = bit_is_set(off_mask.value, button1 - 1)
        if follow:
            # If button1 on and off mask set then turn off button2
            if set_off and new_state:
                return False
            # Else we follow the state as is?????
            return bool(new_state)
        return bool(self._groups[button2].value)

    def _has_follow_leds(self, button):
        """Check if the current button has follow buttons."""
        for follow_button in self._groups:
            if follow_button == button:
                continue
            button_str = f"_{follow_button}" if follow_button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            if not on_mask.is_loaded:
                return False
            follow = bit_is_set(on_mask.value, button - 1)
            if follow:
                return True
        return False

    def _calc_set_leds_command_kwargs(self, led, is_on) -> Dict[str, bool]:
        """Calculate the kwargs values for the SetLedsCommandHandler."""
        leds = {}
        for curr_led in range(1, 9):
            name = f"group{curr_led}"
            if curr_led == led:
                leds[name] = is_on
            else:
                curr_group = self._groups.get(curr_led)
                if curr_group:
                    led_val = self._get_led_follow_state(led, curr_led, is_on)
                else:
                    led_val = False
                leds[name] = led_val
        return leds

    async def _async_update_led_state(
        self,
        group: int,
        value: Union[int, bool],
        event: str,
        led_kwargs: Dict[str, bool],
    ):
        """Set the value of an LED based on the set state and the configuration."""
        if not self._groups.get(group):
            return
        if self._properties[NON_TOGGLE_MASK].value is not None:
            non_toogle = bit_is_set(self._properties[NON_TOGGLE_MASK].value, group)
        else:
            non_toogle = False
        if non_toogle:
            self._groups[group].value = 0
        else:
            self._groups[group].value = value
        self._events[group][event].trigger(value)

        for name, btn_value in led_kwargs.items():
            button = int(name[-1])
            state = self._groups.get(button)
            if state:
                if button == self.load_button and bool(state.value) != btn_value:
                    await self.async_status()
                else:
                    state.value = btn_value

    async def _async_led_follow_check(self, group, on_level):
        """Update LEDs that follow the changed LED."""
        for curr_group, state in self._groups.items():
            if curr_group == group:
                continue
            follow_state = self._get_led_follow_state(group, curr_group, on_level)
            if curr_group == self.load_button and bool(state.value) != follow_state:
                await self.async_status()
            else:
                state.value = follow_state

    def _handle_load_button_property__changed(self, name, value):
        """Handle load button changes."""
        orig_load_button = 1
        for group, state in self._groups.items():
            if state.is_dimmable:
                orig_load_button = group
            if group == value:
                relay_mode = self._operating_flags[RELAY_MODE_OFF].value
                relay_mode = False if relay_mode is None else relay_mode
                state.is_dimmable = not relay_mode
            else:
                state.is_dimmable = False
        load_value = self._groups[orig_load_button].value
        # Set the orig load button on or off
        self._groups[orig_load_button].value = load_value
        self._groups[value].value = load_value
