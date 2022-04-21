"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from functools import partial
from typing import Iterable

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
    LOAD_SENSE_ON,
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
    RESUME_DIM_ON,
    RF_DISABLE_ON,
    SIGNAL_TO_NOISE_FAILURE_COUNT,
    TOGGLE_BUTTON,
    TRIGGER_GROUP_MASK,
    X10_HOUSE,
    X10_OFF,
    X10_UNIT,
)
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
from ..handlers.to_device.set_leds import SetLedsCommandHandler
from ..handlers.to_device.status_request import StatusRequestCommand
from ..utils import bit_is_set, multiple_status, set_bit, set_fan_speed
from .device_commands import (
    GET_LEDS_COMMAND,
    OFF_COMMAND,
    OFF_FAST_COMMAND,
    ON_COMMAND,
    ON_FAST_COMMAND,
    SET_LEDS_COMMAND,
    STATUS_COMMAND,
    STATUS_COMMAND_FAN,
)
from .variable_controller_base import ON_LEVEL_MANAGER
from .variable_responder_base import VariableResponderBase


class DimmableLightingControl(VariableResponderBase):
    """Dimmable Lighting Control Device."""

    def _register_handlers_and_managers(self):
        """Register command handlers and managers."""
        super()._register_handlers_and_managers()
        self._handlers[STATUS_COMMAND] = StatusRequestCommand(
            self._address, status_type=2
        )
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group]["manual_change"] = ManualChangeInbound(
                    self._address, group
                )

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe methods to handlers and managers."""
        super()._subscribe_to_handelers_and_managers()
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group]["manual_change"].subscribe(
                    self._async_on_manual_change
                )

    async def _async_on_manual_change(self):
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


class DimmableLightingControl_SwitchLinc(DimmableLightingControl):
    """SwichLinc based dimmable lights."""

    def _register_op_flags_and_props(self):

        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_OFF, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)

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


class DimmableLightingControl_ToggleLinc(DimmableLightingControl):
    """SwichLinc based dimmable lights."""

    def _register_op_flags_and_props(self):

        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)

        if self._firmware >= 0x3A:
            self._add_property(LED_DIMMING, 2, 3)
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


class DimmableLightingControl_InLineLinc(DimmableLightingControl_SwitchLinc):
    """InLineLinc based dimmable lights."""


class DimmableLightingControl_OutletLinc(DimmableLightingControl):
    """OutletLinc based dimmable lights."""

    def __init__(self, address, cat, subcat, firmware=0, description="", model=""):
        """Init the DimmableLightingControl_OutletLinc class."""
        buttons = {1: DIMMABLE_OUTLET}
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


class DimmableLightingControl_FanLinc(DimmableLightingControl):
    """FanLinc model 2475F Dimmable Lighting Control.

    Device Class 0x01 subcat 0x2e

    """

    def __init__(self, address, cat, subcat, firmware=0, description="", model=""):
        """Init the DimmableLightingControl_FanLinc class."""
        buttons = {1: DIMMABLE_LIGHT, 2: DIMMABLE_FAN}
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

    async def async_status(self):
        """Request the status fo the light and the fan."""
        light_status = await super().async_status()
        fan_status = await self.async_fan_status()
        if light_status == fan_status == ResponseStatus.SUCCESS:
            return ResponseStatus.SUCCESS
        if ResponseStatus.UNCLEAR in (light_status, fan_status):
            return ResponseStatus.UNCLEAR
        return ResponseStatus.FAILURE

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


# TODO setup operating flags for each KPL button
# TODO trigger scenes
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

    async def async_on(self, on_level: int = 0xFF, group: int = 0, fast: bool = False):
        """Turn on the button LED."""
        if group in [0, 1]:
            result = await super().async_on(on_level=on_level, group=group, fast=fast)
        else:
            kwargs = self._change_led_status(led=group, is_on=True)
            result = await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)
        if result == ResponseStatus.SUCCESS:
            event = ON_FAST_EVENT if fast else ON_EVENT
            self._update_leds(group=group, value=on_level, event=event)
        elif result == ResponseStatus.UNCLEAR:
            await self.async_status()
        return result

    async def async_off(self, group: int = 0, fast: bool = False):
        """Turn off the button LED."""
        if group in [0, 1]:
            result = await super().async_off(group=group, fast=fast)
        else:
            kwargs = self._change_led_status(led=group, is_on=False)
            result = await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)
        if result == ResponseStatus.SUCCESS:
            event = OFF_FAST_EVENT if fast else OFF_EVENT
            self._update_leds(group=group, value=0, event=event)
        elif result == ResponseStatus.UNCLEAR:
            await self.async_status()
        return result

    async def async_status(self):
        """Check the status of the device."""
        retries = 5
        status = ResponseStatus.UNSENT
        while retries and status != ResponseStatus.SUCCESS:
            status0 = await super().async_status()
            status1 = await self._handlers[GET_LEDS_COMMAND].async_send()
            status = multiple_status(status0, status1)
            retries -= 1
        return status

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
                on_mask.load(0)
                off_mask.load(0)
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
            if on_mask.is_loaded and off_mask.is_loaded:
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
            toggle_mask.load(0)
            on_off_mask.load(0)

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
        self._handlers[GET_LEDS_COMMAND] = StatusRequestCommand(
            self._address, status_type=1
        )
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group]["manual_change"] = ManualChangeInbound(
                    self._address, group
                )

    def _register_groups(self):
        for button in self._buttons:
            name = self._buttons[button]
            if button == 1:
                self._groups[button] = OnLevel(
                    name=name, address=self._address, group=button
                )
            else:
                self._groups[button] = OnOff(
                    name=name, address=self._address, group=button
                )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[GET_LEDS_COMMAND].subscribe(self._led_status)
        for group in self._buttons:
            if group != 1:
                led_method = partial(self._led_follow_check, group=group)
                self._managers[group][ON_LEVEL_MANAGER].subscribe(led_method)

    def _led_follow_check(self, group, on_level):
        """Check the other LEDs to confirm if they follow the effected LED."""
        for button in self._buttons:
            if button == group:
                continue
            button_str = f"_{button}" if button != 1 else ""
            on_mask = self._properties[f"{ON_MASK}{button_str}"]
            off_mask = self._properties[f"{OFF_MASK}{button_str}"]
            follow = bit_is_set(on_mask, group)
            set_off = bit_is_set(off_mask, group)
            if follow:
                if set_off:
                    self._groups[button].value = 0
                else:
                    self._groups[button].value = on_level

    def _change_led_status(self, led, is_on):
        leds = {}
        for curr_led in range(1, 9):
            var = f"group{curr_led}"
            curr_group = self._groups.get(curr_led)
            curr_val = bool(curr_group.value) if curr_group else False
            leds[var] = is_on if curr_led == led else curr_val
        return leds

    def _update_leds(self, group, value, event):
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
            button = self._buttons[group]
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
            1: DIMMABLE_LIGHT_MAIN,
            3: ON_OFF_SWITCH_A,
            4: ON_OFF_SWITCH_B,
            5: ON_OFF_SWITCH_C,
            6: ON_OFF_SWITCH_D,
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
            1: DIMMABLE_LIGHT_MAIN,
            2: ON_OFF_SWITCH_B,
            3: ON_OFF_SWITCH_C,
            4: ON_OFF_SWITCH_D,
            5: ON_OFF_SWITCH_E,
            6: ON_OFF_SWITCH_F,
            7: ON_OFF_SWITCH_G,
            8: ON_OFF_SWITCH_H,
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
