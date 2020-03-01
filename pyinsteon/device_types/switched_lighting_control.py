"""Switched Lighting Control devices (CATEGORY 0x02)."""
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT
from ..extended_property import LED_DIMMING, X10_HOUSE, X10_UNIT
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

# from ..handlers.to_device.trigger_scene_on import TriggerSceneOnCommandHandler
# from ..handlers.to_device.trigger_scene_off import TriggerSceneOffCommandHandler
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
)
from .commands import SET_LEDS_COMMAND, STATUS_COMMAND
from .on_off_responder_base import OnOffResponderBase


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
            return await super().async_on(group=group)
        kwargs = self._change_led_status(led=group, on=True)
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    async def async_off(self, group: int = 0):
        """Turn off the button LED."""
        if group in [0, 1]:
            return await super().async_off(group=group)
        kwargs = self._change_led_status(led=group, on=False)
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[SET_LEDS_COMMAND] = SetLedsCommandHandler(address=self.address)

    def _register_groups(self):
        super()._register_groups()
        for button in self._buttons:
            name = self._buttons[button]
            self._groups[button] = OnOff(name=name, address=self._address, group=button)

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._handlers[SET_LEDS_COMMAND].subscribe(self._update_leds)

    def _change_led_status(self, led, on):
        leds = {}
        for curr_led in range(1, 9):
            var = "group{}".format(curr_led)
            leds[var] = on if curr_led == led else bool(self._groups.get(curr_led))
        return leds

    def _update_leds(self, group, value):
        self._groups[group].value = value


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
            button=buttons,
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
        self._handlers[self.BOTTOM_GROUP][STATUS_COMMAND] = StatusRequestCommand(
            self._address, 0
        )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()

        self._handlers[self.TOP_GROUP][STATUS_COMMAND].subscribe(
            self._handle_top_status
        )
        self._handlers[self.TOP_GROUP][STATUS_COMMAND].subscribe(
            self._handle_bottom_status
        )

    def _handle_status(self, db_version, status):
        """Set the status of the top and bottom outlets state."""
        self._groups[self.TOP_GROUP].value = status & 0x02
        self._groups[self.BOTTOM_GROUP].value = status & 0x01

    def _handle_top_status(self, db_version, status):
        """Set the status of the top outlet."""
        self._groups[self.TOP_GROUP].value = status

    def _handle_bottom_status(self, db_version, status):
        """Set the status of the bottom outlet."""
        self._groups[self.BOTTOM_GROUP].value = status
