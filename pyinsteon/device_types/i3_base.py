"""I3 device base classes."""

import asyncio
from collections import namedtuple
from typing import Dict, List, Tuple, Union

from ..config import (
    ACK_A_SCENE,
    BLUE_LED_OFF,
    BRIGHTNESS_MAX,
    BRIGHTNESS_MIN,
    BRIGHTNESS_START,
    CLEANUP_REPORT_OFF,
    DETACH_LOAD_ON,
    DISABLE_BUTTONS,
    DO_NOT_ROTATE_TO_OFF,
    GREEN_LED_OFF,
    INSTEON_OFF,
    KEY_BEEP_ON,
    LED_BLINK_ON_ERROR_ON,
    LED_BLINK_ON_TX_ON,
    LED_BRIGHTNESS,
    LED_OFF,
    NIGHT_MODE_LED_BRIGHTNESS,
    NIGHT_MODE_MAX_LEVEL,
    NIGHT_MODE_ON,
    NIGHT_MODE_RAMP_RATE,
    NO_CACHE,
    NON_TOGGLE_MASK,
    NON_TOGGLE_ON_OFF_MASK,
    OFF_MASK,
    ON_LEVEL,
    ON_MASK,
    OPERATING_FLAGS,
    PROGRAM_LOCK_ON,
    RAMP_RATE,
    RED_LED_OFF,
    RELAY_AT_FULL_ON,
    RELAY_MODE_OFF,
    RESUME_DIM_ON,
    RF_DISABLE_ON,
    SKIP_SOME_HOPS,
    TEND_ON,
    UNUSED,
    YAKETY_YAK,
)
from ..config.extended_property import ExtendedProperty
from ..config.op_flag_property_byte import OpFlagPropertyByte
from ..config.operating_flag import OperatingFlag
from ..constants import PropertyType, ResponseStatus
from ..groups.on_level import OnLevel
from ..handlers.from_device.manual_change import ManualChangeInbound
from ..handlers.from_device.off_at_ramp_rate import OffAtRampRateInbound
from ..handlers.from_device.on_at_ramp_rate import OnAtRampRateInbound
from ..handlers.to_device.factory_reset import FactoryResetCommand
from ..handlers.to_device.night_mode_off import NightModeOffCommand
from ..handlers.to_device.night_mode_on import NightModeOnCommand
from ..managers.ext_prop_read_manager import ExtendedPropertyReadManager
from ..managers.ext_prop_write_manager import ExtendedPropertyWriteManager
from ..utils import multiple_status
from .device_commands import MANUAL_CHANGE, OFF_AT_RAMP_RATE, ON_AT_RAMP_RATE
from .on_off_responder_base import OnOffResponderBase
from .variable_responder_base import VariableResponderBase

OP_FLAG_1F_00 = f"{OPERATING_FLAGS}_1f_00"
OP_FLAG_1F_05 = f"{OPERATING_FLAGS}_1f_05"
OP_FLAG_DATA_4 = f"{OPERATING_FLAGS}_data_4"

READ_MGRS = "ext_prop_read_mgrs"
WRITE_MGRS = "ext_prop_write_mgrs"
NIGHT_MODE_OFF = "night_mode_off"

OpsFlagDef = namedtuple(
    "OpsFlagDef", ["name", "group", "bit", "set_cmd", "unset_cmd", "prop_type"]
)
ExtPropDef = namedtuple(
    "ExtPropDef", ["name", "value_type", "is_read_only", "prop_type", "op_flags"]
)
ExtPropReadDef = namedtuple("ExtPropReadDef", ["cmd2", "data1", "data2", "data3"])
ExtPropRespDef = namedtuple(
    "ExtPropRespDef", ["cmd2", "data1", "data2", "data3", "props_dict"]
)
ExtPropWriteDef = namedtuple(
    "ExtPropWriteDef", ["cmd2", "data1", "data2", "props_dict"]
)


##############################################################################
# This section defines the default operating flags, extened properties and
# extened properties readers and writers.
##############################################################################
def default_i3_ops_flags(
    dimmable: bool, additional_flags: List[OpsFlagDef]
) -> List[OpsFlagDef]:
    """Return a list of default operating flags for i3 devices."""
    show = PropertyType.STANDARD if dimmable else PropertyType.HIDDEN
    def_flags = [
        # Group 0
        OpsFlagDef(PROGRAM_LOCK_ON, 0, 0, 0x00, 0x01, PropertyType.STANDARD),
        OpsFlagDef(LED_BLINK_ON_TX_ON, 0, 1, 0x02, 0x03, PropertyType.STANDARD),
        OpsFlagDef(RESUME_DIM_ON, 0, 2, 0x04, 0x05, show),
        OpsFlagDef(f"{UNUSED}_0_3", 0, 3, None, None, PropertyType.HIDDEN),
        OpsFlagDef(LED_OFF, 0, 4, 0x08, 0x09, PropertyType.STANDARD),
        OpsFlagDef(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B, PropertyType.STANDARD),
        OpsFlagDef(RF_DISABLE_ON, 0, 6, 0x0C, 0x0D, PropertyType.ADVANCED),
        # SHOULD NEVER USE IT WILL MAKE THE DEVICE UNRESPONSIVE
        # However, it can be set with 20 0F if you really want to
        OpsFlagDef(INSTEON_OFF, 0, 7, None, None, PropertyType.HIDDEN),
        # Group 5
        OpsFlagDef(TEND_ON, 5, 0, None, None, PropertyType.HIDDEN),
        # -- Night mode is set with (cmd1: 0x3B  cmd2: 0xXX) and (cmd2: 0x3C  cmd2: 0xXX)
        OpsFlagDef(NIGHT_MODE_ON, 5, 1, None, None, PropertyType.STANDARD),
        OpsFlagDef(LED_BLINK_ON_ERROR_ON, 5, 2, None, None, PropertyType.STANDARD),
        OpsFlagDef(CLEANUP_REPORT_OFF, 5, 3, None, None, PropertyType.HIDDEN),
        OpsFlagDef(DISABLE_BUTTONS, 5, 4, None, None, PropertyType.HIDDEN),
        # -- Unsetting Detached load does not work with the documented command 20 1B
        # -- So setting as read_only but can be set via OP_FLAG_1F_05
        OpsFlagDef(DETACH_LOAD_ON, 5, 5, 0x1B, 0x1A, PropertyType.HIDDEN),
        OpsFlagDef(ACK_A_SCENE, 5, 6, 0x1C, 0x1D, PropertyType.HIDDEN),
        OpsFlagDef(RELAY_MODE_OFF, 5, 7, 0x1E, 0x1F, show),
        # Group 7
        OpsFlagDef(YAKETY_YAK, 7, 0, None, None, PropertyType.HIDDEN),
        OpsFlagDef(RED_LED_OFF, 7, 1, 0x28, 0x29, PropertyType.STANDARD),
        OpsFlagDef(SKIP_SOME_HOPS, 7, 2, 0x2A, 0x2B, PropertyType.HIDDEN),
        OpsFlagDef(GREEN_LED_OFF, 7, 3, 0x2C, 0x2D, PropertyType.STANDARD),
        OpsFlagDef(BLUE_LED_OFF, 7, 4, 0x2E, 0x2F, PropertyType.STANDARD),
        OpsFlagDef(NO_CACHE, 7, 5, 0x30, 0x31, PropertyType.HIDDEN),
        OpsFlagDef(DO_NOT_ROTATE_TO_OFF, 7, 6, 0x32, 0x33, show),
        OpsFlagDef(RELAY_AT_FULL_ON, 7, 7, None, None, PropertyType.HIDDEN),
        # Group 9 (KPL Only?)
        OpsFlagDef(f"{NIGHT_MODE_ON}_kpl", 9, 0, None, None, PropertyType.HIDDEN),
        OpsFlagDef(f"{NO_CACHE}_kpl", 9, 1, None, None, PropertyType.HIDDEN),
    ]
    # Create an index of the group and bit of the additional flags
    add_flag_set: List[Tuple[int, int]] = []
    for add_flag in additional_flags:
        add_flag_set.append((add_flag.group, add_flag.bit))

    # Remove duplicates keeping the additional flag
    flags = [flag for flag in def_flags if (flag.group, flag.bit) not in add_flag_set]
    flags.extend(additional_flags)
    return flags


def operating_flag_ext_prop_def(
    group: int,
    operating_flags: List[OperatingFlag],
    op_flags_def: List[OpsFlagDef],
) -> Dict[int, OperatingFlag]:
    """Return a dictionary of operating flags for use in an Extended Property byte."""
    op_flag_byte_def = get_op_flags_by_group(group=group, op_flags=op_flags_def)
    return {index: operating_flags[name] for index, name in op_flag_byte_def.items()}


def default_i3_ext_props(
    dimmable,
    operating_flags: List[OperatingFlag],
    op_flags_def: List[OpsFlagDef],
    op_flags_data_4: Dict[int, str],
    buttons: Union[List[int], None] = None,
) -> List[ExtPropDef]:
    """Return a list of default extended properties for i3 devices."""
    show_dim = PropertyType.STANDARD if dimmable else PropertyType.HIDDEN
    show_dim_adv = PropertyType.ADVANCED if dimmable else PropertyType.HIDDEN

    op_flag_byte_00_dict = operating_flag_ext_prop_def(0, operating_flags, op_flags_def)
    op_flag_byte_05_dict = operating_flag_ext_prop_def(5, operating_flags, op_flags_def)
    op_flag_byte_data_4_dict = {
        bit: operating_flags[name] for bit, name in op_flags_data_4.items()
    }

    props = [
        ExtPropDef(NIGHT_MODE_LED_BRIGHTNESS, int, False, PropertyType.STANDARD, None),
        ExtPropDef(NIGHT_MODE_RAMP_RATE, int, False, PropertyType.STANDARD, None),
        ExtPropDef(LED_BRIGHTNESS, int, False, PropertyType.STANDARD, None),
        ExtPropDef(BRIGHTNESS_MIN, int, False, show_dim, None),
        ExtPropDef(BRIGHTNESS_MAX, int, False, show_dim, None),
        ExtPropDef(BRIGHTNESS_START, int, False, show_dim, None),
        ExtPropDef(NIGHT_MODE_MAX_LEVEL, int, False, PropertyType.STANDARD, None),
        ExtPropDef(
            OP_FLAG_1F_00,
            None,
            None,
            PropertyType.HIDDEN,
            op_flags=op_flag_byte_00_dict,
        ),
        ExtPropDef(
            OP_FLAG_1F_05,
            None,
            None,
            PropertyType.HIDDEN,
            op_flags=op_flag_byte_05_dict,
        ),
        ExtPropDef(
            OP_FLAG_DATA_4,
            int,
            False,
            PropertyType.HIDDEN,
            op_flags=op_flag_byte_data_4_dict,
        ),
    ]
    if buttons:
        for button in buttons:
            if button == 1:
                on_mask = ON_MASK
                off_mask = OFF_MASK
                ramp_rate = RAMP_RATE
                on_level = ON_LEVEL
            else:
                on_mask = f"{ON_MASK}_{button}"
                off_mask = f"{OFF_MASK}_{button}"
                ramp_rate = f"{RAMP_RATE}_{button}"
                on_level = f"{ON_LEVEL}_{button}"
            props.append(ExtPropDef(on_mask, int, False, PropertyType.ADVANCED, None))
            props.append(ExtPropDef(off_mask, int, False, PropertyType.ADVANCED, None))
            props.append(ExtPropDef(ramp_rate, int, False, PropertyType.ADVANCED, None))
            props.append(ExtPropDef(on_level, int, False, PropertyType.STANDARD, None))

        props.append(
            ExtPropDef(NON_TOGGLE_MASK, int, False, PropertyType.ADVANCED, None)
        )
        props.append(
            ExtPropDef(NON_TOGGLE_ON_OFF_MASK, int, False, PropertyType.ADVANCED, None)
        )
    else:
        props.append(ExtPropDef(RAMP_RATE, int, False, show_dim_adv, None))
        props.append(ExtPropDef(ON_LEVEL, int, False, show_dim, None))

    return props


def properties_2e_00_xx_00_def(
    properties: Dict[str, ExtendedProperty], groups: List[int]
) -> List[Tuple[ExtPropReadDef, ExtPropRespDef, List[ExtPropWriteDef]]]:
    """Return a set of properties that represent the 2E 00 XX 00 properties."""
    if 0 not in groups and 1 not in groups:
        raise ValueError(
            "Properties for 2E 00 XX 00 reader/writes requires either buttons 0 or 1."
        )
    prop_group_read_resp_def: List[Tuple[ExtPropReadDef, ExtPropRespDef]] = []
    for group in groups:
        props: Dict[int, ExtendedProperty] = {}
        writers: List[ExtPropWriteDef] = []
        if group in [0, 1]:
            props[7] = properties[RAMP_RATE]
            props[8] = properties[ON_LEVEL]
            props[9] = properties[LED_BRIGHTNESS]
            writers.append(
                ExtPropWriteDef(0x00, group, 0x05, {3: properties[RAMP_RATE]})
            )
            writers.append(
                ExtPropWriteDef(0x00, group, 0x06, {3: properties[ON_LEVEL]})
            )
            writers.append(
                ExtPropWriteDef(0x00, 0x00, 0x07, {3: properties[LED_BRIGHTNESS]})
            )
        if group == 1:
            props[3] = properties[ON_MASK]
            props[4] = properties[OFF_MASK]
            props[10] = properties[NON_TOGGLE_MASK]
            props[13] = properties[NON_TOGGLE_ON_OFF_MASK]
            writers.append(ExtPropWriteDef(0x00, group, 0x02, {3: properties[ON_MASK]}))
            writers.append(
                ExtPropWriteDef(0x00, group, 0x03, {3: properties[OFF_MASK]})
            )
            writers.append(
                ExtPropWriteDef(0x00, 0x00, 0x08, {3: properties[NON_TOGGLE_MASK]})
            )
            writers.append(
                ExtPropWriteDef(
                    0x00, 0x00, 0x0B, {3: properties[NON_TOGGLE_ON_OFF_MASK]}
                )
            )
        elif group not in [0, 1]:
            props[3] = properties[f"{ON_MASK}_{group}"]
            props[4] = properties[f"{OFF_MASK}_{group}"]
            props[7] = properties[f"{RAMP_RATE}_{group}"]
            props[8] = properties[f"{ON_LEVEL}_{group}"]
            writers.append(
                ExtPropWriteDef(
                    0x00, group, 0x02, {3: properties[f"{ON_MASK}_{group}"]}
                )
            )
            writers.append(
                ExtPropWriteDef(
                    0x00, group, 0x03, {3: properties[f"{OFF_MASK}_{group}"]}
                )
            )
            writers.append(
                ExtPropWriteDef(
                    0x00, group, 0x05, {3: properties[f"{RAMP_RATE}_{group}"]}
                )
            )
            writers.append(
                ExtPropWriteDef(
                    0x00, group, 0x06, {3: properties[f"{ON_LEVEL}_{group}"]}
                )
            )
        read_def = ExtPropReadDef(0x00, group, 0x00, 0x00)
        resp_def = ExtPropRespDef(0x00, group, 0x01, None, props)
        prop_group_read_resp_def.append((read_def, resp_def, writers))
    return prop_group_read_resp_def


def properties_2e_01_reader_writer_def(
    properties: Dict[str, ExtendedProperty], resp_data_1: int
) -> Tuple[ExtPropReadDef, ExtPropRespDef, ExtPropWriteDef]:
    """Return a set of properties that represent the 2E 01 properties."""
    props_dict = {
        2: properties[OP_FLAG_1F_00],
        3: properties[OP_FLAG_1F_05],
        4: properties[OP_FLAG_DATA_4],
        5: properties[RAMP_RATE],
        6: properties[ON_LEVEL],
        7: properties[LED_BRIGHTNESS],
        8: properties[BRIGHTNESS_MAX],
        9: properties[BRIGHTNESS_MIN],
        10: properties[BRIGHTNESS_START],
        11: properties[NIGHT_MODE_MAX_LEVEL],
        12: properties[NIGHT_MODE_LED_BRIGHTNESS],
        13: properties[NIGHT_MODE_RAMP_RATE],
    }
    read_def = ExtPropReadDef(0x01, 0x00, 0x00, 0x00)
    resp_def = ExtPropRespDef(0x01, resp_data_1, None, None, props_dict)
    writer_def = ExtPropWriteDef(0x01, 0x02, None, props_dict)
    return read_def, resp_def, writer_def


def get_op_flags_by_group(group: int, op_flags: List[OpsFlagDef]) -> Dict[int, str]:
    """Return a dictionary of bit and operating flag bit definition by group."""
    return {flag.bit: flag.name for flag in op_flags if flag.group == group}


##############################################################################
# End of default Operating Flags and Extended Properties definition section
##############################################################################


# pylint: disable=no-member
# pylint: disable=super-with-arguments
class I3Base:
    """I3 device type base class."""

    _is_kpl: bool = False
    _op_flags_data_4: Dict[int, str] = {
        0: YAKETY_YAK,
        1: RED_LED_OFF,
        2: SKIP_SOME_HOPS,
        3: GREEN_LED_OFF,
        4: BLUE_LED_OFF,
        5: NO_CACHE,
        6: DO_NOT_ROTATE_TO_OFF,
        7: RELAY_AT_FULL_ON,
    }  # used for 2E 01 read and write command

    def __init__(
        self, address, cat, subcat, firmware=0x00, description="", model="", **kwargs
    ):
        """Init the DeviceBattery class."""

        # The super class is a Device class such as VariableResponderBase
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
        for mgr in self._managers[READ_MGRS]:
            response = await mgr.async_send()
            responses.append(response)
            await asyncio.sleep(0.2)
        return multiple_status(*responses)

    async def async_write_op_flags(self) -> ResponseStatus:
        """Write the operating flags to the device."""
        responses = []
        if prop := self._operating_flags.get(NIGHT_MODE_ON):
            if prop.is_dirty:
                response = await self.async_set_night_mode(prop.new_value)
                responses.append(response)
        response = await self._op_flags_manager.async_write()
        responses.append(response)
        return multiple_status(*responses)

    async def async_write_ext_properties(self) -> ResponseStatus:
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

    async def async_factory_reset(self) -> ResponseStatus:
        """Reset this device to factory defaults."""
        cmd = FactoryResetCommand(self._address, self._cat, self._subcat)
        return await cmd.async_send()

    def _register_handlers_and_managers(self) -> None:
        super(I3Base, self)._register_handlers_and_managers()
        self._managers[NIGHT_MODE_ON] = NightModeOnCommand(self._address)
        self._managers[NIGHT_MODE_OFF] = NightModeOffCommand(self._address)
        groups = list(self._groups) if self._is_kpl else [0]
        reader_writer_groups = properties_2e_00_xx_00_def(self._properties, groups)
        for prop_reader, prop_resp, prop_writers in reader_writer_groups:
            self._add_ext_prop_read_manager(
                properties=prop_resp.props_dict,
                cmd2=prop_reader.cmd2,
                data1_read=prop_reader.data1,
                data2_read=prop_reader.data2,
                data3_read=prop_reader.data3,
                data1_resp=prop_resp.data1,
                data2_resp=prop_resp.data2,
                data3_resp=prop_resp.data3,
            )
            for prop_writer in prop_writers:
                self._add_ext_prop_write_manager(
                    properties=prop_writer.props_dict,
                    cmd2=prop_writer.cmd2,
                    data1=prop_writer.data1,
                    data2=prop_writer.data2,
                )

        # Cat   Subcat  Model   Device      Data1
        # 0x01  0x57    PS01    i3 Paddle   0x05
        # 0x01	0x58    DS01    i3 Dial     0x04
        # 0x01	0x59    KP014   i3 Keypad   0x01
        # 0x02	0x3F    WR01    i3 Outlet   0x03
        data2_map = {
            (0x01, 0x57): 0x05,
            (0x01, 0x58): 0x04,
            (0x01, 0x59): 0x01,
            (0x02, 0x3F): 0x03,
        }
        data_1_resp = data2_map.get((self._cat, self._subcat))
        if not data_1_resp:
            raise ValueError("Cannot find data 1 value for the 2E 01 message response.")
        prop_reader, prop_resp, prop_writer = properties_2e_01_reader_writer_def(
            self._properties, data_1_resp
        )
        self._add_ext_prop_read_manager(
            properties=prop_resp.props_dict,
            cmd2=prop_reader.cmd2,
            data1_read=prop_reader.data1,
            data2_read=prop_reader.data2,
            data3_read=prop_reader.data3,
            data1_resp=prop_resp.data1,
            data2_resp=prop_resp.data2,
            data3_resp=prop_resp.data3,
        )
        self._add_ext_prop_write_manager(
            properties=prop_writer.props_dict,
            cmd2=prop_writer.cmd2,
            data1=prop_writer.data1,
            data2=prop_writer.data2,
        )

    def _subscribe_to_handelers_and_managers(self) -> None:
        super(I3Base, self)._subscribe_to_handelers_and_managers()
        self._managers[NIGHT_MODE_ON].subscribe(self._handle_night_mode)
        self._managers[NIGHT_MODE_OFF].subscribe(self._handle_night_mode)

    def _handle_night_mode(self, night_mode) -> None:
        """Handle the night mode on/off response."""
        if prop := self._operating_flags.get(NIGHT_MODE_ON):
            prop.set_value(night_mode)

    def _register_default_op_flags_and_props(
        self,
        dimmable: bool,
        additional_flags: List[OpsFlagDef],
    ) -> None:
        # Adding operating flags
        flags = default_i3_ops_flags(dimmable, additional_flags)
        for flag in flags:
            self._add_operating_flag(
                name=flag.name,
                group=flag.group,
                bit=flag.bit,
                set_cmd=flag.set_cmd,
                unset_cmd=flag.unset_cmd,
                prop_type=flag.prop_type,
            )
        # Need to set Night Mode as read/write because it is not updated with a 0x20 command
        self._operating_flags[NIGHT_MODE_ON].is_read_only = False
        flag_names = [
            LED_BLINK_ON_ERROR_ON,
            CLEANUP_REPORT_OFF,
            DISABLE_BUTTONS,
            NIGHT_MODE_ON,
            DETACH_LOAD_ON,
            DO_NOT_ROTATE_TO_OFF,
            RELAY_AT_FULL_ON,
        ]
        for name in flag_names:
            flag = self._operating_flags.get(name)
            if flag:
                flag.is_read_only = False

        # Adding extended properties
        buttons = list(self._groups) if self._is_kpl else None
        for prop in default_i3_ext_props(
            dimmable, self._operating_flags, flags, self._op_flags_data_4, buttons
        ):
            if prop.op_flags:
                self._properties[prop.name] = OpFlagPropertyByte(
                    address=self._address, name=prop.name, flags=prop.op_flags
                )
            else:
                self._properties[prop.name] = ExtendedProperty(
                    address=self._address,
                    name=prop.name,
                    value_type=prop.value_type,
                    is_reversed=False,
                    is_read_only=prop.is_read_only,
                    prop_type=prop.prop_type,
                )

    def _add_ext_prop_read_manager(
        self,
        properties: Dict[int, ExtendedProperty],
        cmd2: int = 0,
        data1_read: int = 0,
        data2_read: int = 0,
        data3_read: int = None,
        data1_resp: int = 0,
        data2_resp: int = 1,
        data3_resp: int = None,
    ) -> None:
        self._managers[READ_MGRS] = self._managers.get(READ_MGRS, [])
        self._managers[READ_MGRS].append(
            ExtendedPropertyReadManager(
                address=self._address,
                properties=properties,
                cmd2=cmd2,
                data1_read=data1_read,
                data2_read=data2_read,
                data3_read=data3_read,
                data1_resp=data1_resp,
                data2_resp=data2_resp,
                data3_resp=data3_resp,
            )
        )

    def _add_ext_prop_write_manager(
        self,
        properties: Dict[int, ExtendedProperty],
        data2: Union[int, None],
        cmd2: int = 0,
        data1: int = 0,
    ) -> None:
        self._managers[WRITE_MGRS] = self._managers.get(WRITE_MGRS, [])
        self._managers[WRITE_MGRS].append(
            ExtendedPropertyWriteManager(
                address=self._address,
                properties=properties,
                cmd2=cmd2,
                data1=data1,
                data2=data2,
            )
        )


# pylint: disable=super-with-arguments
class I3VariableResponderBase(I3Base, VariableResponderBase):
    """I3 variable responder base class."""

    def _register_op_flags_and_props(self) -> None:
        self._register_default_op_flags_and_props(dimmable=True, additional_flags=[])

    def _register_handlers_and_managers(self) -> None:
        super()._register_handlers_and_managers()
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group][ON_AT_RAMP_RATE] = OnAtRampRateInbound(
                    self._address, group
                )
                self._handlers[group][OFF_AT_RAMP_RATE] = OffAtRampRateInbound(
                    self._address, group
                )
                self._handlers[group][MANUAL_CHANGE] = ManualChangeInbound(
                    self._address, group
                )

    def _subscribe_to_handelers_and_managers(self) -> None:
        super()._subscribe_to_handelers_and_managers()
        for group, group_prop in self._groups.items():
            if isinstance(group_prop, OnLevel):
                self._handlers[group][MANUAL_CHANGE].subscribe(self.async_status)
                # pylint: disable=cell-var-from-loop
                self._handlers[group][OFF_AT_RAMP_RATE].subscribe(
                    lambda on_level, ramp_rate: self._handle_on_off_at_ramp_rate(
                        group, on_level, ramp_rate
                    ),
                    force_strong_ref=True,
                )
                self._handlers[group][ON_AT_RAMP_RATE].subscribe(
                    lambda on_level, ramp_rate: self._handle_on_off_at_ramp_rate(
                        group, on_level, ramp_rate
                    ),
                    force_strong_ref=True,
                )

    def _handle_on_off_at_ramp_rate(self, group: int, on_level: int, ramp_rate: int):
        """Handle the on and off at ramp rate inbound broadcast messages."""
        self._groups[group].set_value(on_level)


# pylint: disable=super-with-arguments
class I3OnOffResponderBase(I3Base, OnOffResponderBase):
    """I3 on/off responder base class."""

    def _register_op_flags_and_props(self) -> None:
        self._register_default_op_flags_and_props(dimmable=False, additional_flags=[])
