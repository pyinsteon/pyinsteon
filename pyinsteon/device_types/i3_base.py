"""I3 device base classes."""
import asyncio
from collections import namedtuple
from typing import Dict, List

from ..config import (
    ACK_A_SCENE,
    BLUE_LED_OFF,
    BRIGHTNESS_MAX,
    BRIGHTNESS_MIN,
    BRIGHTNESS_START,
    CLEANUP_REPORT_OFF,
    DETACH_LOAD_ON,
    DISABLE_BUTTONS,
    GREEN_LED_OFF,
    INSTEON_OFF,
    KEY_BEEP_ON,
    LED_BLINK_ON_ERROR_ON,
    LED_BLINK_ON_TX_ON,
    LED_BRIGHTNESS,
    LED_OFF,
    LOAD_SENSE_2_ON,
    LOAD_SENSE_ON,
    MOD_SYNC_SYNC,
    NIGHT_LEDS_ON,
    NIGHT_MODE_LED_BRIGHTNESS,
    NIGHT_MODE_MAX_LEVEL,
    NIGHT_MODE_ON,
    NIGHT_MODE_RAMP_RATE,
    NO_CACHE,
    ON_LEVEL,
    OPS_FLAGS_PROPERTY,
    PROGRAM_LOCK_ON,
    RAMP_RATE,
    RED_LED_OFF,
    RELAY_MODE_OFF,
    RESUME_DIM_ON,
    RF_DISABLE_ON,
    SKIP_SOME_HOPS,
    TEND_ON,
    USE_LOCAL_PROFILE,
    YAKETY_YAK,
)
from ..config.extended_property import ExtendedProperty
from ..config.op_flag_property_byte import OpFlagPropertyByte
from ..config.operating_flag import OperatingFlag
from ..constants import PropertyType, ResponseStatus
from ..handlers.to_device.night_mode_off import NightModeOffCommand
from ..handlers.to_device.night_mode_on import NightModeOnCommand
from ..managers.ext_prop_read_manager import ExtendedPropertyReadManager
from ..managers.ext_prop_write_manager import ExtendedPropertyWriteManager
from ..utils import multiple_status
from .on_off_responder_base import OnOffResponderBase
from .variable_responder_base import VariableResponderBase

OP_FLAG_PROP_1 = f"{OPS_FLAGS_PROPERTY}_1"
OP_FLAG_PROP_2 = f"{OPS_FLAGS_PROPERTY}_2"
OP_FLAG_PROP_3 = f"{OPS_FLAGS_PROPERTY}_3"

READ_MGRS = "ext_prop_read_mgrs"
WRITE_MGRS = "ext_prop_write_mgrs"
NIGHT_MODE_OFF = "night_mode_off"

OpsFlagDef = namedtuple(
    "OpsFlagDef", ["name", "group", "bit", "set_cmd", "unset_cmd", "prop_type"]
)
ExtProp = namedtuple("ExtProp", ["name", "value_type", "is_read_only", "prop_type"])


def _default_ops_flags(dimmable: bool) -> List[OpsFlagDef]:
    """Return a list of default operating flags for i3 devices."""
    return [
        # Group 0
        OpsFlagDef(PROGRAM_LOCK_ON, 0, 0, 0x00, 0x01, PropertyType.STANDARD),
        OpsFlagDef(LED_BLINK_ON_TX_ON, 0, 1, 0x02, 0x03, PropertyType.STANDARD),
        OpsFlagDef(LED_OFF, 0, 4, 0x08, 0x09, PropertyType.STANDARD),
        OpsFlagDef(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B, PropertyType.STANDARD),
        OpsFlagDef(RF_DISABLE_ON, 0, 6, 0x0C, 0x0D, PropertyType.ADVANCED),
        OpsFlagDef(INSTEON_OFF, 0, 7, 0x0E, 0x0F, PropertyType.ADVANCED),
        # Group 5
        OpsFlagDef(TEND_ON, 5, 0, None, None, PropertyType.HIDDEN),
        # -- Night mode is set with (cmd1: 0x3B  cmd2: 0xXX) and (cmd2: 0x3C  cmd2: 0xXX)
        OpsFlagDef(NIGHT_MODE_ON, 5, 1, None, None, PropertyType.HIDDEN),
        OpsFlagDef(LED_BLINK_ON_ERROR_ON, 5, 2, None, None, PropertyType.ADVANCED),
        OpsFlagDef(CLEANUP_REPORT_OFF, 5, 3, None, None, PropertyType.HIDDEN),
        OpsFlagDef(DISABLE_BUTTONS, 5, 4, None, None, PropertyType.HIDDEN),
        # -- DETACH_LOAD_ON: future feature set/unset with 0x12, 0x13
        OpsFlagDef(DETACH_LOAD_ON, 5, 5, 0x12, 0x13, PropertyType.HIDDEN),
        OpsFlagDef(ACK_A_SCENE, 5, 6, 0x1C, 0x1D, PropertyType.HIDDEN),
        OpsFlagDef(RELAY_MODE_OFF, 5, 7, 0x1E, 0x1F, PropertyType.HIDDEN),
        # Group 7
        OpsFlagDef(YAKETY_YAK, 7, 0, None, None, PropertyType.HIDDEN),
        OpsFlagDef(RED_LED_OFF, 7, 1, 0x28, 0x29, PropertyType.STANDARD),
        OpsFlagDef(SKIP_SOME_HOPS, 7, 2, 0x2A, 0x2B, PropertyType.HIDDEN),
        OpsFlagDef(GREEN_LED_OFF, 7, 3, 0x2C, 0x0D, PropertyType.STANDARD),
        OpsFlagDef(BLUE_LED_OFF, 7, 4, 0x2E, 0x2F, PropertyType.STANDARD),
        OpsFlagDef(NO_CACHE, 7, 5, 0x30, 0x31, PropertyType.HIDDEN),
    ]


def _default_ext_props(dimmable=True) -> List[ExtProp]:
    """Return a list of default extended properties for i3 devices."""
    show_dim = PropertyType.STANDARD if dimmable else PropertyType.HIDDEN
    show_dim_adv = PropertyType.ADVANCED if dimmable else PropertyType.HIDDEN
    return [
        ExtProp(NIGHT_MODE_LED_BRIGHTNESS, int, False, PropertyType.HIDDEN),
        ExtProp(NIGHT_MODE_RAMP_RATE, int, False, PropertyType.HIDDEN),
        ExtProp(RAMP_RATE, int, False, show_dim_adv),
        ExtProp(ON_LEVEL, int, False, show_dim),
        ExtProp(LED_BRIGHTNESS, int, False, PropertyType.STANDARD),
        ExtProp(BRIGHTNESS_MIN, int, False, PropertyType.HIDDEN),
        ExtProp(BRIGHTNESS_MAX, int, False, PropertyType.HIDDEN),
        ExtProp(BRIGHTNESS_START, int, False, PropertyType.HIDDEN),
        ExtProp(NIGHT_MODE_MAX_LEVEL, int, False, PropertyType.HIDDEN),
    ]


# pylint: disable=no-member
# pylint: disable=super-with-arguments
class I3Base:
    """I3 device type base class."""

    def __init__(
        self, address, cat, subcat, firmware=0x00, description="", model="", **kwargs
    ):
        """Init the DeviceBattery class."""

        # The super class is the non-battery base class such as OnOffControllerBase
        super(I3Base, self).__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
            **kwargs,
        )

    async def async_read_ext_properties(self, group=None) -> ResponseStatus:
        """Get the device extended properties."""
        responses = []
        for _, mgr in self._managers[READ_MGRS].items():
            response = await mgr.async_send()
            responses.append(response)
        await asyncio.sleep(0.5)
        return multiple_status(*responses)

    async def async_write_op_flags(self):
        """Write the operating flags to the device."""
        responses = []
        if prop := self._operating_flags.get(NIGHT_MODE_ON):
            if prop.is_dirty:
                response = await self.async_set_night_mode(prop.new_value)
                responses.append(response)
        response = await self._op_flags_manager.async_write()
        responses.append(response)
        return multiple_status(*responses)

    async def async_write_ext_properties(self):
        """Write the extended properties."""
        responses = [ResponseStatus.SUCCESS]
        for cmd in self._managers[WRITE_MGRS]:
            if cmd.is_dirty:
                responses.append(await cmd.async_write())
        return multiple_status(*responses)

    async def async_set_night_mode(self, on: bool) -> ResponseStatus:
        """Set the device night mode on or off."""
        cmd = NIGHT_MODE_ON if on else NIGHT_MODE_OFF
        for _ in range(0, 3):
            response = await self._managers[cmd].async_send()
            await asyncio.sleep(0.5)
        return response

    def _register_handlers_and_managers(self):
        super(I3Base, self)._register_handlers_and_managers()
        self._managers[NIGHT_MODE_ON] = NightModeOnCommand(self._address)
        self._managers[NIGHT_MODE_OFF] = NightModeOffCommand(self._address)
        self._register_default_ext_prop_read_managers()
        self._register_default_ext_prop_write_managers()

    def _subscribe_to_handelers_and_managers(self):
        super(I3Base, self)._subscribe_to_handelers_and_managers()
        self._managers[NIGHT_MODE_ON].subscribe(self._handle_night_mode)
        self._managers[NIGHT_MODE_OFF].subscribe(self._handle_night_mode)

    def _handle_night_mode(self, night_mode) -> None:
        """Handle the night mode on/off response."""
        if prop := self._operating_flags.get(NIGHT_MODE_ON):
            prop.load(night_mode)

    def _register_default_op_flags_and_props(
        self,
        dimmable: bool,
        ops_flags_1: Dict[int, str],
        ops_flags_2: Dict[int, str],
        ops_flags_3: Dict[int, str],
    ):
        for flag in _default_ops_flags(dimmable):
            self._add_operating_flag(
                name=flag.name,
                group=flag.group,
                bit=flag.bit,
                set_cmd=flag.set_cmd,
                unset_cmd=flag.unset_cmd,
                prop_type=flag.prop_type,
            )
        self._operating_flags[NIGHT_MODE_ON].is_read_only = False
        for prop in _default_ext_props(dimmable):
            self._properties[prop.name] = ExtendedProperty(
                address=self._address,
                name=prop.name,
                value_type=prop.value_type,
                is_reversed=False,
                is_read_only=prop.is_read_only,
                prop_type=prop.prop_type,
            )
        # Dummy flag needed for Extended Properties group 1
        self._operating_flags[MOD_SYNC_SYNC] = OperatingFlag(
            address=self._address,
            name=MOD_SYNC_SYNC,
            value_type=bool,
            prop_type=PropertyType.HIDDEN,
        )
        self._operating_flags[NIGHT_LEDS_ON] = OperatingFlag(
            address=self._address,
            name=NIGHT_LEDS_ON,
            value_type=bool,
            prop_type=PropertyType.HIDDEN,
        )
        ops_flags_1_all = {
            0: PROGRAM_LOCK_ON,
            1: LED_BLINK_ON_TX_ON,
            4: LED_OFF,
            5: KEY_BEEP_ON,
            6: RF_DISABLE_ON,
            7: INSTEON_OFF,
        }
        ops_flags_1_all.update(ops_flags_1)
        ops_flags_2_all = {
            1: NIGHT_MODE_ON,
            2: LED_BLINK_ON_ERROR_ON,
            3: CLEANUP_REPORT_OFF,
            4: DISABLE_BUTTONS,
            5: DETACH_LOAD_ON,
            6: ACK_A_SCENE,
            7: RELAY_MODE_OFF,
        }
        ops_flags_2_all.update(ops_flags_2)
        ops_flags_3_all = {
            0: YAKETY_YAK,
            1: MOD_SYNC_SYNC,
            2: SKIP_SOME_HOPS,
            3: RELAY_MODE_OFF,
            4: NIGHT_LEDS_ON,
            5: NO_CACHE,
        }
        ops_flags_3_all.update(ops_flags_3)
        self._add_extended_prop_byte(OP_FLAG_PROP_1, ops_flags_1_all)
        self._add_extended_prop_byte(OP_FLAG_PROP_2, ops_flags_2_all)
        self._add_extended_prop_byte(OP_FLAG_PROP_3, ops_flags_3_all)

    def _add_extended_prop_byte(self, name: str, op_flag_map: Dict[int, str]):
        """Add an extended property to hold the operating flags used in an extended write."""
        ops_flags = {
            index: self._operating_flags[name] for index, name in op_flag_map.items()
        }
        self._properties[name] = OpFlagPropertyByte(
            address=self._address, name=name, flags=ops_flags
        )

    def _register_default_ext_prop_read_managers(self):
        group_0 = {
            7: self._properties[RAMP_RATE],
            8: self._properties[ON_LEVEL],
            9: self._properties[LED_BRIGHTNESS],
        }
        self._managers[READ_MGRS] = self._managers.get(READ_MGRS, {})
        self._managers[READ_MGRS][0] = ExtendedPropertyReadManager(
            address=self._address,
            properties=group_0,
            cmd2=0x00,
            data1_read=0x00,
            data2_read=0x00,
            data3_read=0x00,
            data1_resp=0x00,
            data2_resp=0x01,
            data3_resp=None,
        )
        # group_1 = {
        #     2: self._properties[OP_FLAG_PROP_1],
        #     3: self._properties[OP_FLAG_PROP_2],
        #     4: self._properties[OP_FLAG_PROP_3],
        #     # 5: self._properties[RAMP_RATE],
        #     # 6: self._properties[ON_LEVEL],
        #     # 7: self._properties[LED_BRIGHTNESS],
        #     8: self._properties[BRIGHTNESS_MAX],
        #     9: self._properties[BRIGHTNESS_MIN],
        #     10: self._properties[BRIGHTNESS_START],
        #     11: self._properties[NIGHT_MODE_MAX_LEVEL],
        #     12: self._properties[NIGHT_MODE_LED_BRIGHTNESS],
        #     13: self._properties[NIGHT_MODE_RAMP_RATE],
        # }
        # self._managers[READ_MGRS][1] = ExtendedPropertyReadManager(
        #     address=self._address,
        #     properties=group_1,
        #     cmd2=0x01,
        #     data1_read=0x00,
        #     data2_read=0x00,
        #     data3_read=0x00,
        #     data1_resp=0x01,
        #     data2_resp=None,
        #     data3_resp=None,
        # )

    def _register_default_ext_prop_write_managers(self):
        self._managers[WRITE_MGRS] = self._managers.get(WRITE_MGRS, [])

        led = {3: self._properties[LED_BRIGHTNESS]}
        self._managers[WRITE_MGRS].append(
            ExtendedPropertyWriteManager(
                address=self._address, properties=led, cmd2=0, data1=0x01, data2=0x07
            )
        )

        on_level = {3: self._properties[ON_LEVEL]}
        self._managers[WRITE_MGRS].append(
            ExtendedPropertyWriteManager(
                address=self._address,
                properties=on_level,
                cmd2=0,
                data1=0x01,
                data2=0x06,
            )
        )
        ramp_rate = {3: self._properties[RAMP_RATE]}
        self._managers[WRITE_MGRS].append(
            ExtendedPropertyWriteManager(
                address=self._address,
                properties=ramp_rate,
                cmd2=0,
                data1=0x01,
                data2=0x05,
            )
        )


# pylint: disable=super-with-arguments
class I3VariableResponderBase(I3Base, VariableResponderBase):
    """I3 variable responder base class."""

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(RESUME_DIM_ON, 0, 2, 4, 5)
        self._add_operating_flag(
            USE_LOCAL_PROFILE, 0, 3, 6, 7, prop_type=PropertyType.ADVANCED
        )
        self._register_default_op_flags_and_props(
            dimmable=True,
            ops_flags_1={2: RESUME_DIM_ON, 3: USE_LOCAL_PROFILE},
            ops_flags_2={},
            ops_flags_3={},
        )


# pylint: disable=super-with-arguments
class I3OnOffResponderBase(I3Base, OnOffResponderBase):
    """I3 on/off responder base class."""

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(
            LOAD_SENSE_ON, 0, 2, 4, 5, prop_type=PropertyType.ADVANCED
        )
        self._add_operating_flag(
            LOAD_SENSE_2_ON, 0, 3, 6, 7, prop_type=PropertyType.ADVANCED
        )
        self._register_default_op_flags_and_props(
            dimmable=True,
            ops_flags_1={2: LOAD_SENSE_ON, 3: LOAD_SENSE_2_ON},
            ops_flags_2={},
            ops_flags_3={},
        )
