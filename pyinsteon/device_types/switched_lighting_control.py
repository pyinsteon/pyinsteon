"""Switched Lighting Control devices (CATEGORY 0x02)."""
from functools import partial
from typing import Iterable

from ..constants import ResponseStatus
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT
from ..extended_property import (
    LED_DIMMING,
    X10_HOUSE,
    X10_UNIT,
    ON_MASK,
    OFF_MASK,
    NON_TOGGLE_MASK,
    NON_TOGGLE_ON_OFF_MASK,
    TRIGGER_GROUP_MASK,
)
from ..groups import (
    ON_OFF_OUTLET_BOTTOM,
    ON_OFF_OUTLET_TOP,
    ON_OFF_SWITCH,
    ON_OFF_SWITCH_A,
    ON_OFF_SWITCH_B,
    ON_OFF_SWITCH_C,
    ON_OFF_SWITCH_D,
    ON_OFF_SWITCH_E,
    ON_OFF_SWITCH_F,
    ON_OFF_SWITCH_G,
    ON_OFF_SWITCH_H,
    ON_OFF_SWITCH_MAIN,
)
from ..groups.on_off import OnOff
from ..handlers.to_device.set_leds import SetLedsCommandHandler
from ..handlers.to_device.status_request import StatusRequestCommand
from ..operating_flag import (
    DUAL_LINE_ON,
    KEY_BEEP_ON,
    LED_BLINK_ON_ERROR_ON,
    LED_BLINK_ON_TX_ON,
    LED_ON,
    MOMENTARY_LINE_ON,
    PROGRAM_LOCK_ON,
    RESUME_DIM_ON,
    REVERSED_ON,
    THREE_WAY_ON,
    RF_DISABLE_ON,
    POWERLINE_DISABLE_ON,
)
from .commands import SET_LEDS_COMMAND, STATUS_COMMAND, GET_LEDS_COMMAND
from .on_off_responder_base import OnOffResponderBase
from ..utils import bit_is_set, set_bit, multiple_status
from .on_off_controller_base import ON_LEVEL_MANAGER


class SwitchedLightingControl(OnOffResponderBase):
    """Switched Lighting Control device."""

    def __init__(
        self,
        address,
        cat,
        subcat,
        firmware=0x00,
        description="",
        model="",
        buttons=None,
        state_name=ON_OFF_SWITCH,
        on_event_name=ON_EVENT,
        off_event_name=OFF_EVENT,
        on_fast_event_name=ON_FAST_EVENT,
        off_fast_event_name=OFF_FAST_EVENT,
    ):
        """Init the OnOffResponderBase class."""
        buttons = {1: ON_OFF_SWITCH} if buttons is None else buttons
        super().__init__(
            address,
            cat,
            subcat,
            firmware,
            description,
            model,
            buttons,
            on_event_name,
            off_event_name,
            on_fast_event_name,
            off_fast_event_name,
        )


class SwitchedLightingControl_ApplianceLinc(SwitchedLightingControl):
    """ApplianceLinc based dimmable lights."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)


class SwitchedLightingControl_SwitchLinc(SwitchedLightingControl):
    """SwichLinc based dimmable lights."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)

        self._add_property(LED_DIMMING, 3, 3)
        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)


class SwitchedLightingControl_ToggleLinc(SwitchedLightingControl):
    """ToggleLinc based on/off lights."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)

        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)


class SwitchedLightingControl_InLineLinc(SwitchedLightingControl_SwitchLinc):
    """InLineLinc based dimmable lights."""


class SwitchedLightingControl_OutletLinc(SwitchedLightingControl):
    """OutletLinc based dimmable lights."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)

        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)


class SwitchedLightingControl_Micro(SwitchedLightingControl):
    """Micro switch based dimmable lights."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)

        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 2, 2, 0x15, 0x14)

        self._add_operating_flag(DUAL_LINE_ON, 3, 0, 0x1E, 0x1F)
        self._add_operating_flag(MOMENTARY_LINE_ON, 3, 1, 0x20, 0x21)
        self._add_operating_flag(THREE_WAY_ON, 3, 2, 0x23, 0x22)
        self._add_operating_flag(REVERSED_ON, 3, 3, 0x25, 0x24)


class SwitchedLightingControl_DinRail(SwitchedLightingControl):
    """DINRail based dimmable lights."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)

        self._add_property(LED_DIMMING, 3, 3)
        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)


class SwitchedLightingControl_KeypadLinc(SwitchedLightingControl):
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
        """Init the SwitchedLightingControl_KeypadLinc class."""
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )

    async def async_on(self, group: int = 0):
        """Turn on the button LED."""
        if group in [0, 1]:
            result = await super().async_on(group=group)
        else:
            kwargs = self._change_led_status(led=group, is_on=True)
            result = await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)
        if result == ResponseStatus.SUCCESS:
            self._update_leds(group=group, value=0xFF, event=ON_EVENT)
        elif result == ResponseStatus.UNCLEAR:
            await self.async_status()
        return result

    async def async_off(self, group: int = 0):
        """Turn off the button LED."""
        if group in [0, 1]:
            result = await super().async_off(group=group)
        else:
            kwargs = self._change_led_status(led=group, is_on=False)
            result = await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)
        if result == ResponseStatus.SUCCESS:
            self._update_leds(group=group, value=0, event=OFF_EVENT)
        elif result == ResponseStatus.UNCLEAR:
            await self.async_status()
        return result

    async def async_status(self, group=None):
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

    def set_toggle_mode(self, button: int, mode: int):
        """Set the toggle mode of a button.

        Usage:
            button: Integer of the button number
            mode: Integer of the mode
                0: Toggle
                1: Non-Toggle ON only
                2: Non-Toggle OFF only
        """
        if button not in self._buttons.keys():
            raise ValueError(f"Button {button} not in button list.")
        if mode not in [0, 1, 2]:
            raise ValueError(f"Mode {mode} invalid. Valid mode are [0, 1, 2]")

        toggle_mask = self.properties[NON_TOGGLE_MASK]
        on_off_mask = self.properties[NON_TOGGLE_ON_OFF_MASK]
        if not toggle_mask.is_loaded or not on_off_mask.is_loaded:
            toggle_mask.load(0)
            on_off_mask.load(0)
        if mode == 0:
            toggle_mask.new_value = set_bit(toggle_mask.value, button - 1, False)
            on_off_mask.new_value = set_bit(on_off_mask.value, button - 1, False)
        elif mode == 1:
            toggle_mask.new_value = set_bit(toggle_mask.value, button - 1, True)
            on_off_mask.new_value = set_bit(on_off_mask.value, button - 1, True)
        else:
            toggle_mask.new_value = set_bit(toggle_mask.value, button - 1, True)
            on_off_mask.new_value = set_bit(on_off_mask.value, button - 1, False)

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[SET_LEDS_COMMAND] = SetLedsCommandHandler(address=self.address)
        self._handlers[GET_LEDS_COMMAND] = StatusRequestCommand(
            self._address, status_type=1
        )

    def _register_groups(self):
        super()._register_groups()
        for button in self._buttons:
            name = self._buttons[button]
            self._groups[button] = OnOff(name=name, address=self._address, group=button)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[GET_LEDS_COMMAND].subscribe(self._led_status)
        for group in self._buttons:
            if self._groups.get(group) is not None:
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
            var = "group{}".format(curr_led)
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

    def _register_operating_flags(self):
        """Register operating flags."""
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(RF_DISABLE_ON, 0, 6, 0x0C, 0x0D)
        self._add_operating_flag(POWERLINE_DISABLE_ON, 0, 7, 0x0E, 0x0F)
        self._add_operating_flag(
            LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15, is_reversed=True
        )

        self._add_property(LED_DIMMING, 9, 7, 1)
        self._add_property(NON_TOGGLE_MASK, 0x0A, 0x08)
        self._add_property(NON_TOGGLE_ON_OFF_MASK, 0x0D, 0x0B)
        self._add_property(TRIGGER_GROUP_MASK, 0x0E, 0x0C)
        for button in self._buttons:
            button_str = f"_{button}" if button != 1 else ""
            self._add_property(f"{ON_MASK}{button_str}", 3, 2, button)
            self._add_property(f"{OFF_MASK}{button_str}", 4, 3, button)
            self._add_property(f"{X10_HOUSE}{button_str}", 5, None, button)
            self._add_property(f"{X10_UNIT}{button_str}", 6, None, button)


class SwitchedLightingControl_KeypadLinc_6(SwitchedLightingControl_KeypadLinc):
    """KeypadLinc 6 button switch."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the SwitchedLightingControl_KeypadLinc_6 class."""
        buttons = {
            1: ON_OFF_SWITCH_MAIN,
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


class SwitchedLightingControl_KeypadLinc_8(SwitchedLightingControl_KeypadLinc):
    """KeypadLinc 8 button switch."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the SwitchedLightingControl_KeypadLinc_8 class."""
        buttons = {
            1: ON_OFF_SWITCH_MAIN,
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


class SwitchedLightingControl_OnOffOutlet(SwitchedLightingControl_ApplianceLinc):
    """On/Off outlet model 2663-222 Switched Lighting Control.

    Device Class 0x02 subcat 0x39
    """

    TOP_GROUP = 1
    BOTTOM_GROUP = 2

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the SwitchedLightingControl_KeypadLinc class."""
        buttons = {1: ON_OFF_OUTLET_TOP, 2: ON_OFF_OUTLET_BOTTOM}
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )

    def status(self, group=None):
        """Request the status of the device."""
        if group is None:
            self._handlers[STATUS_COMMAND].send()
        if group in [1, 2]:
            self._handlers[group][STATUS_COMMAND].send()

    async def async_status(self, group=None):
        """Request the status of the device."""
        if group is None:
            return await self._handlers[STATUS_COMMAND].async_send()
        if group in [1, 2]:
            return await self._handlers[group][STATUS_COMMAND].async_send()

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[STATUS_COMMAND] = StatusRequestCommand(self._address, 1)

        if self._handlers.get(self.TOP_GROUP) is None:
            self._handlers[self.TOP_GROUP] = {}
        self._handlers[self.TOP_GROUP][STATUS_COMMAND] = StatusRequestCommand(
            self._address, 0
        )

        if self._handlers.get(self.BOTTOM_GROUP) is None:
            self._handlers[self.BOTTOM_GROUP] = {}
        self._handlers[self.BOTTOM_GROUP][STATUS_COMMAND] = self._handlers[
            STATUS_COMMAND
        ]

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()

        self._handlers[self.TOP_GROUP][STATUS_COMMAND].subscribe(
            self._handle_top_status
        )

        self._handlers[STATUS_COMMAND].subscribe(self._handle_status)

    def _handle_top_status(self, db_version, status):
        """Set the status of the top outlet."""
        self._groups[self.TOP_GROUP].value = status

    def _handle_status(self, db_version, status):
        """Set the status of the top and bottom outlets."""
        self._groups[self.TOP_GROUP].value = 1 if (status & 0x01) else 0
        self._groups[self.BOTTOM_GROUP].value = 1 if (status & 0x02) else 0
