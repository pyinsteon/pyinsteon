"""Dimmable Lighting Control Devices (CATEGORY 0x01)."""
from ..constants import FanSpeed
from ..extended_property import LED_DIMMING, ON_LEVEL, RAMP_RATE, X10_HOUSE, X10_UNIT

# from ..handlers.to_device.trigger_scene_on import TriggerSceneOnCommandHandler
# from ..handlers.to_device.trigger_scene_off import TriggerSceneOffCommandHandler
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
from ..groups.on_off import OnOff
from ..handlers import ResponseStatus
from ..handlers.to_device.set_leds import SetLedsCommandHandler
from ..handlers.to_device.status_request import StatusRequestCommand
from ..operating_flag import (
    CLEANUP_REPORT_ON,
    CRC_ERROR_COUNT,
    DATABASE_DELTA,
    KEY_BEEP_ON,
    LED_BLINK_ON_ERROR_ON,
    LED_BLINK_ON_TX_ON,
    LED_ON,
    LOAD_SENSE_ON,
    POWERLINE_DISABLE_ON,
    PROGRAM_LOCK_ON,
    RESUME_DIM_ON,
    RF_DISABLE_ON,
    SIGNAL_TO_NOISE_FAILURE_COUNT,
    X10_OFF,
)
from .variable_responder_base import VariableResponderBase

from .commands import (  # TRIGGER_SCENE_ON_COMMAND,; TRIGGER_SCENE_OFF_COMMAND,
    OFF_COMMAND,
    OFF_FAST_COMMAND,
    ON_COMMAND,
    ON_FAST_COMMAND,
    SET_LEDS_COMMAND,
    STATUS_COMMAND_FAN,
)


class DimmableLightingControl(VariableResponderBase):
    """Dimmable Lighting Control Device."""


class DimmableLightingControl_LampLinc(DimmableLightingControl):
    """LampLinc based dimmable lights."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)
        self._add_operating_flag(LOAD_SENSE_ON, 0, 5, 0x0A, 0x0B)

        self._add_property(LED_DIMMING, 3, 3)
        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)


class DimmableLightingControl_SwitchLinc(DimmableLightingControl):
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
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)


class DimmableLightingControl_ToggleLinc(DimmableLightingControl):
    """SwichLinc based dimmable lights."""

    def _register_operating_flags(self):

        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15)

        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)


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

    def _register_operating_flags(self):
        super()._register_operating_flags()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)

        self._add_property(X10_HOUSE, 5, None)
        self._add_property(X10_UNIT, 6, None)


class DimmableLightingControl_DinRail(DimmableLightingControl):
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
        self._add_property(RAMP_RATE, 7, 5)
        self._add_property(ON_LEVEL, 8, 6)


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
        self._handlers[group][command].send(on_level=on_level)

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
        return await self._handlers[group][command].async_send(on_level)

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

    def status(self):
        """Request the status of the light and the fan."""
        super().status()
        self.fan_status()

    async def async_status(self):
        """Request the status fo the light and the fan."""
        light_status = await super().async_status()
        fan_status = await self.async_fan_status()
        if light_status == fan_status == ResponseStatus.SUCCESS:
            return ResponseStatus.SUCCESS
        if (
            light_status == ResponseStatus.UNCLEAR
            or fan_status == ResponseStatus.UNCLEAR
        ):
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

    def _register_operating_flags(self):
        super()._register_operating_flags()

        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_BLINK_ON_TX_ON, 0, 1, 2, 3)
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(LED_ON, 0, 4, 8, 9, is_reversed=True)
        self._add_operating_flag(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B)
        self._add_operating_flag(RF_DISABLE_ON, 0, 6, 0x0C, 0x0D)
        self._add_operating_flag(POWERLINE_DISABLE_ON, 0, 7, 0x0E, 0x0F)

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
            self._groups[2].set_value(FanSpeed.OFF)
        elif int(status) <= int(FanSpeed.LOW):
            self._groups[2].set_value(FanSpeed.LOW)
        elif int(status) <= int(FanSpeed.MEDIUM):
            self._groups[2].set_value(FanSpeed.MEDIUM)
        else:
            self._groups[2].set_value(FanSpeed.HIGH)


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
            return await super().async_on(on_level=on_level, group=group, fast=fast)
        kwargs = self._change_led_status(led=group, is_on=True)
        return await self._handlers[SET_LEDS_COMMAND].async_send(**kwargs)

    async def async_off(self, group: int = 0, fast: bool = False):
        """Turn off the button LED."""
        if group in [0, 1]:
            return await super().async_off(group=group, fast=fast)
        kwargs = self._change_led_status(led=group, is_on=False)
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

    def _change_led_status(self, led, is_on):
        leds = {}
        for curr_led in range(1, 9):
            var = "group{}".format(curr_led)
            leds[var] = is_on if curr_led == led else bool(self._groups.get(curr_led))
        return leds

    def _update_leds(self, group, value):
        self._groups[group].value = value


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
