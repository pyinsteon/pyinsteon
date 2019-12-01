"""Switched Lighting Control devices (CATEGORY 0x02)."""
from ..events import OFF_EVENT, OFF_FAST_EVENT, ON_EVENT, ON_FAST_EVENT
from ..handlers.to_device.set_leds import SetLedsCommandHandler
from ..handlers.to_device.trigger_scene import TriggerSceneCommandHandler
from ..states import (ON_OFF_OUTLET_BOTTOM, ON_OFF_OUTLET_TOP, ON_OFF_SWITCH,
                      ON_OFF_SWITCH_B, ON_OFF_SWITCH_C, ON_OFF_SWITCH_D,
                      ON_OFF_SWITCH_E, ON_OFF_SWITCH_F, ON_OFF_SWITCH_G,
                      ON_OFF_SWITCH_H, ON_OFF_SWITCH_MAIN)
from ..states.on_off import OnOff
from .commands import SET_LEDS_COMMAND, STATUS_COMMAND, TRIGGER_SCENE_COMMAND
from .on_off_responder_base import OnOffResponderBase


class SwitchedLightingControl(OnOffResponderBase):
    """Switched Lighting Control device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=None, state_name=ON_OFF_SWITCH,
                 on_event_name=ON_EVENT, off_event_name=OFF_EVENT,
                 on_fast_event_name=ON_FAST_EVENT, off_fast_event_name=OFF_FAST_EVENT):
        """Init the OnOffResponderBase class."""
        buttons = {1: ON_OFF_SWITCH} if buttons is None else buttons
        super().__init__(address, cat, subcat, firmware, description, model, buttons,
                         on_event_name, off_event_name, on_fast_event_name, off_fast_event_name)

    def _register_default_links(self):
        from ..managers.link_manager import DefaultLink
        super()._register_default_links()
        link0 = DefaultLink(False, 0, 0x00, 0x00, 0x00,
                            self._cat, self.subcat, self.firmware)
        link1 = DefaultLink(True, 1, 0xff, 0x1c, 0x01, 0x00, 0x00, 0x00)
        self._default_links.append(link0)
        self._default_links.append(link1)

class SwitchedLightingControl_ApplianceLinc(SwitchedLightingControl):
    """ApplianceLinc based dimmable lights."""

    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_BLINK_ON_TX_ON, LED_ON)

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit4', 0)  # 10
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9)


class SwitchedLightingControl_SwitchLinc(SwitchedLightingControl):
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


class SwitchedLightingControl_InLineLinc(SwitchedLightingControl_SwitchLinc):
    """InLineLinc based dimmable lights."""


class SwitchedLightingControl_OutletLinc(SwitchedLightingControl):
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


class SwitchedLightingControl_Micro(SwitchedLightingControl):
    """Micro switch based dimmable lights."""

    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_BLINK_ON_TX_ON, LED_ON, KEY_BEEP_ON,
                                      DUAL_LINE_ON, MOMENTARY_LINE_ON, THREE_WAY_ON, REVERSED_ON,
                                      LED_BLINK_ON_ERROR_ON)

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit4', 0)  # 10
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0a, 0x0b)

        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 2, 2, 0x15, 0x14)

        self._add_operating_flag(DUAL_LINE_ON, 3, 0, 0x1e, 0x1f)
        self._add_operating_flag(MOMENTARY_LINE_ON, 3, 1, 0x20, 0x21)
        self._add_operating_flag(THREE_WAY_ON, 3, 2, 0x23, 0x22)
        self._add_operating_flag(REVERSED_ON, 3, 3, 0x25, 0x24)

class SwitchedLightingControl_DinRail(SwitchedLightingControl):
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


class SwitchedLightingControl_KeypadLinc(SwitchedLightingControl):
    """KeypadLinc base class."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model='', buttons=None):
        super().__init__(address, cat, subcat, firmware, description, model, buttons=buttons)

    async def async_on(self, group: int = 0):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_on(group=group)
        kwargs = self._change_led_status(led=group, on=True)
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    async def async_off(self, group: int = 0):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_off(group=group)
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
            name = '{}_{}'.format(ON_OFF_SWITCH, self._button_list[button])
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


class SwitchedLightingControl_KeypadLinc_6(SwitchedLightingControl_KeypadLinc):
    """KeypadLinc 6 button switch."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the SwitchedLightingControl_KeypadLinc_6 class."""
        buttons = {1: ON_OFF_SWITCH_MAIN,
                   3: ON_OFF_SWITCH_A,
                   4: ON_OFF_SWITCH_B,
                   5: ON_OFF_SWITCH_C,
                   6: ON_OFF_SWITCH_D}
        super().__init__(address=address, cat=cat, subcat=subcat, firmware=firmware,
                         description=description, model=model, buttons=buttons)


class SwitchedLightingControl_KeypadLinc_8(SwitchedLightingControl_KeypadLinc):
    """KeypadLinc 8 button switch."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the SwitchedLightingControl_KeypadLinc_8 class."""
        buttons = {1: ON_OFF_SWITCH_MAIN,
                   2: ON_OFF_SWITCH_B,
                   3: ON_OFF_SWITCH_C,
                   4: ON_OFF_SWITCH_D,
                   5: ON_OFF_SWITCH_E,
                   6: ON_OFF_SWITCH_F,
                   7: ON_OFF_SWITCH_G,
                   8: ON_OFF_SWITCH_H}
        super().__init__(address=address, cat=cat, subcat=subcat, firmware=firmware,
                         description=description, model=model, button=buttons)

class SwitchedLightingControl_OnOffOutlet(SwitchedLightingControl_ApplianceLinc):
    """On/Off outlet model 2663-222 Switched Lighting Control.

    Device Class 0x02 subcat 0x39
    """

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the SwitchedLightingControl_KeypadLinc class."""
        buttons = {1: ON_OFF_OUTLET_TOP, 2: ON_OFF_OUTLET_BOTTOM}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=buttons)

    def status(self, group=None):
        """Request the status of the device."""
        self._handlers[STATUS_COMMAND].send(status_type=1)

    async def async_status(self, group=None):
        """Request the status of the device."""
        return await self._handlers[STATUS_COMMAND].async_send(status_type=1)

    def _set_status(self, status):
        """Set the status of the dimmable_switch state."""
        self._states[1].value = status & 0x02
        self._states[2].value = status & 0x01
