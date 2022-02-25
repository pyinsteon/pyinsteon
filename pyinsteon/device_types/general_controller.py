"""General controller devices (cat: 0x00)."""
from ..aldb.no_aldb import NoALDB
from ..config import (
    GROUPED_ON,
    KEY_BEEP_ON,
    LED_ON,
    PROGRAM_LOCK_ON,
    SEND_ON_ONLY,
    STAY_AWAKE_ON,
)
from ..constants import ResponseStatus
from ..groups import (
    ON_OFF_SWITCH_A,
    ON_OFF_SWITCH_B,
    ON_OFF_SWITCH_C,
    ON_OFF_SWITCH_D,
    ON_OFF_SWITCH_E,
    ON_OFF_SWITCH_F,
    ON_OFF_SWITCH_G,
    ON_OFF_SWITCH_H,
)
from .battery_base import BatteryDeviceBase
from .device_base import Device
from .variable_controller_base import VariableControllerBase


class GeneralController(Device):
    """General controller device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the GeneralController class."""

        super().__init__(address, cat, subcat, firmware, description, model)
        self._aldb = NoALDB(self._address)


class GeneralController_ControlLinc(VariableControllerBase):
    """ControLinc 2430 device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the GeneralController_ControlLinc class."""
        buttons = {
            1: ON_OFF_SWITCH_A,
            2: ON_OFF_SWITCH_B,
            3: ON_OFF_SWITCH_C,
            4: ON_OFF_SWITCH_D,
            5: ON_OFF_SWITCH_E,
            6: ON_OFF_SWITCH_F,
        }
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )


class GeneralController_RemoteLinc(BatteryDeviceBase, VariableControllerBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the GeneralController_RemoteLinc class."""
        buttons = {
            1: ON_OFF_SWITCH_A,
            2: ON_OFF_SWITCH_B,
            3: ON_OFF_SWITCH_C,
            4: ON_OFF_SWITCH_D,
            5: ON_OFF_SWITCH_E,
            6: ON_OFF_SWITCH_F,
        }
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(STAY_AWAKE_ON, 0, 3, 6, 7)


class GeneralController_MiniRemoteBase(BatteryDeviceBase, VariableControllerBase):
    """RemoteLinc 2440 device."""

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
        self._database_delta = 0

    async def async_status(self, group=0):
        """Return success always."""
        return ResponseStatus.SUCCESS

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_ON, 0, 1, 2, 3)
        self._add_operating_flag(KEY_BEEP_ON, 0, 2, 4, 5)
        self._add_operating_flag(STAY_AWAKE_ON, 0, 3, 6, 7)
        self._add_operating_flag(SEND_ON_ONLY, 0, 4, 8, 9)
        self._add_operating_flag(GROUPED_ON, 0, 6, 0x0E, 0x0F)


# TODO setup ability to swich from toggle to button groups
class GeneralController_MiniRemote_Switch(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device with a single button."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the GeneralController_MiniRemote_Switch class."""
        buttons = {1: ON_OFF_SWITCH_A, 2: ON_OFF_SWITCH_B}
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )


class GeneralController_MiniRemote_4(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the GeneralController_MiniRemote_4 class."""
        buttons = {
            1: ON_OFF_SWITCH_A,
            2: ON_OFF_SWITCH_B,
            3: ON_OFF_SWITCH_C,
            4: ON_OFF_SWITCH_D,
        }
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )


class GeneralController_MiniRemote_8(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the GeneralController_MiniRemote_8 class."""
        buttons = {
            1: ON_OFF_SWITCH_B,
            2: ON_OFF_SWITCH_A,
            3: ON_OFF_SWITCH_D,
            4: ON_OFF_SWITCH_C,
            5: ON_OFF_SWITCH_F,
            6: ON_OFF_SWITCH_E,
            7: ON_OFF_SWITCH_H,
            8: ON_OFF_SWITCH_G,
        }
        super().__init__(
            address, cat, subcat, firmware, description, model, buttons=buttons
        )
