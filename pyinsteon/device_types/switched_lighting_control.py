"""Switched Lighting Control devices (CATEGORY 0x02)."""
from ..handlers.kpl.set_leds import SetLedsCommandHandler
from ..handlers.kpl.trigger_scene import TriggerSceneCommandHandler
from .commands import SET_LEDS_COMMAND, TRIGGER_SCENE_COMMAND, STATUS_COMMAND
from .on_off_responder_base import OnOffResponderBase
from ..states import ON_OFF_SWITCH_STATE, ON_OFF_SWITCH_STATE_BOTTOM
from ..states.on_off import OnOff


class SwitchedLightingControl(OnOffResponderBase):
    """Switched Lighting Control device."""

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

    def __init__(self, button_list, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the SwitchedLightingControl_KeypadLinc class."""
        super().__init__(address, cat, subcat, firmware, description, model, buttons=[1])
        for button in button_list:
            name = '{}_{}'.format(ON_OFF_SWITCH_STATE, button_list[button])
            self._states[button] = OnOff(name=name, address=self._address, group=button)
            self._add_button_handlers(button)

    async def async_on(self, group: int = 0):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_on(group=group)
        kwargs = {}
        for curr_group in range(1, 9):
            var = 'group{}'.format(curr_group)
            kwargs[var] = True if curr_group == group else bool(self._states.get(curr_group))
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    async def async_off(self, group: int = 0):
        """Turn on the button LED. """
        if group in [0, 1]:
            return await super().async_off(group=group)
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


class SwitchedLightingControl_KeypadLinc_6(SwitchedLightingControl_KeypadLinc):
    """KeypadLinc 6 button switch."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the SwitchedLightingControl_KeypadLinc_6 class."""
        button_list = {3: 'A', 4: 'B', 5: 'C', 6: 'D'}
        super().__init__(button_list=button_list, address=address, cat=cat, subcat=subcat,
                         firmware=firmware, description=description, model=model)


class SwitchedLightingControl_KeypadLinc_8(SwitchedLightingControl_KeypadLinc):
    """KeypadLinc 8 button switch."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the SwitchedLightingControl_KeypadLinc_8 class."""
        button_list = {2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H'}
        super().__init__(button_list=button_list, address=address, cat=cat, subcat=subcat,
                         firmware=firmware, description=description, model=model)

class SwitchedLightingControl_OnOffOutlet(SwitchedLightingControl_ApplianceLinc):
    """On/Off outlet model 2663-222 Switched Lighting Control.

    Device Class 0x02 subcat 0x39
    """

    def __init__(self, button_list, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the SwitchedLightingControl_KeypadLinc class."""
        super().__init__(address, cat, subcat, firmware, description, model, buttons=[1, 2])

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
