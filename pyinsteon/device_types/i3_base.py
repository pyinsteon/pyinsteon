"""Base class for I3 devices."""
from collections import namedtuple
from typing import Dict, List, Union

from ..config import (
    BUTTONS_DISABLED,
    CLEANUP_REPORT_ON,
    DETACH_LOAD_ON,
    INSTEON_OFF,
    KEY_BEEP_ON,
    LED_BLINK_ON_ERROR_ON,
    LED_BLINK_ON_TX_ON,
    LED_OFF,
    NIGHT_MODE_ON,
    PROGRAM_LOCK_ON,
    RELAY_MODE,
    RF_DISABLE_ON,
    SMART_HOPS_ON,
)
from ..constants import PropertyType
from .on_off_responder_base import OnOffControllerBase
from .variable_controller_base import VariableControllerBase

OpsFlagDef = namedtuple(
    "OpsFlagDef",
    ["name", "group", "bit", "set_cmd", "unset_cmd", "prop_type"],
)
PropertyDef = namedtuple(
    "PropertyDef",
    ["name", "data_field", "set_cmd", "group", "bit", "is_reversed", "prop_type"],
)


def _get_i3_common_op_flags() -> List[Dict[str, Union[str, int, PropertyType]]]:
    """Return a list of Operating Flags common to all I3 devices."""
    ops_flags = (
        # Group 0
        OpsFlagDef(PROGRAM_LOCK_ON, 0, 0, 0, 1, PropertyType.STANDARD),
        OpsFlagDef(LED_BLINK_ON_TX_ON, 0, 1, 2, 3, PropertyType.STANDARD),
        OpsFlagDef(LED_OFF, 0, 4, 8, 9, PropertyType.STANDARD),
        OpsFlagDef(KEY_BEEP_ON, 0, 5, 0x0A, 0x0B, PropertyType.STANDARD),
        OpsFlagDef(RF_DISABLE_ON, 0, 6, 0x0C, 0x0D, PropertyType.ADVANCED),
        OpsFlagDef(INSTEON_OFF, 0, 7, 0x0E, 0x0F, PropertyType.ADVANCED),
        # Group 5
        OpsFlagDef(NIGHT_MODE_ON, 5, 1, 0x3B, 0x3C, PropertyType.STANDARD),
        OpsFlagDef(LED_BLINK_ON_ERROR_ON, 5, 2, 0x14, 0x15, PropertyType.STANDARD),
        OpsFlagDef(CLEANUP_REPORT_ON, 5, 3, 0x16, 0x17, PropertyType.ADVANCED),
        OpsFlagDef(BUTTONS_DISABLED, 5, 4, 0x18, 0x19, PropertyType.ADVANCED),
        OpsFlagDef(DETACH_LOAD_ON, 5, 5, 0x1A, 0x1B, PropertyType.ADVANCED),
        OpsFlagDef(SMART_HOPS_ON, 5, 6, 0x1C, 0x1D, PropertyType.ADVANCED),
        OpsFlagDef(
            RELAY_MODE, 5, 7, 0x1E, 0x1F, PropertyType.STANDARD
        ),  # Is this only relevant for dimmable devices?
    )
    return [flag._asdict() for flag in ops_flags]


def _get_i3_common_properties() -> List[Dict[str, Union[str, int, PropertyType]]]:
    pass


class I3OnOffControllerBase(OnOffControllerBase):
    """Base class for I3 On/Off devices."""

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        for flag in _get_i3_common_op_flags():
            self._add_operating_flag(**flag)


class I3VariableControllerBase(VariableControllerBase):
    """Base class for I3 Variable Level devices."""
