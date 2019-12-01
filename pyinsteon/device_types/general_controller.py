"""General controller devices (cat: 0x00)."""
from . import BatteryDeviceBase, Device
from .variable_controller_base import VariableControllerBase


class GeneralController(Device):
    """General controller device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        """Init the GeneralController class."""
        from ..aldb.no_aldb import NoALDB
        super().__init__(address, cat, subcat, firmware, description, model)
        self._aldb = NoALDB(self._address)


class GeneralController_ControlLinc(VariableControllerBase):
    """ControLinc 2430 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        buttons = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=buttons)


class GeneralController_RemoteLinc(BatteryDeviceBase, VariableControllerBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        buttons = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=buttons)

    def _register_operating_flags(self):
        from ..operating_flag import (STAY_AWAKE_ON)
        super()._register_operating_flags()
        self._remove_operating_flag('bit3', 0)
        self._add_operating_flag(STAY_AWAKE_ON, 0, 3, 6, 7)


class GeneralController_MiniRemoteBase(BatteryDeviceBase, VariableControllerBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=None):
        """Init the GeneralController_MiniRemoteBase class."""
        super().__init__(address, cat, subcat, firmware, description, model, buttons)
        self._database_delta = 0


    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, STAY_AWAKE_ON, SEND_ON_ONLY,
                                      KEY_BEEP_ON, LED_ON, GROUPED_ON)

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)
        self._remove_operating_flag('bit1', 0)
        self._remove_operating_flag('bit2', 0)
        self._remove_operating_flag('bit3', 0)
        self._remove_operating_flag('bit4', 0)
        self._remove_operating_flag('bit6', 0)
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 0, 0, 1)
        self._add_operating_flag(LED_ON, 0, 1, 2, 3)
        self._add_operating_flag(KEY_BEEP_ON, 0, 2, 4, 5)
        self._add_operating_flag(STAY_AWAKE_ON, 0, 3, 6, 7)
        self._add_operating_flag(SEND_ON_ONLY, 0, 4, 8, 9)
        self._add_operating_flag(GROUPED_ON, 0, 6, 0x0e, 0x0f)

# TODO setup ability to swich from toggle to button groups
class GeneralController_MiniRemote_Switch(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device with a single button."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the GeneralController_MiniRemote_Switch class."""
        buttons = {1: None, 2: None}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=buttons)


class GeneralController_MiniRemote_4(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        buttons = {1: None, 2: None, 3: None, 4: None}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=buttons)


class GeneralController_MiniRemote_8(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        buttons = {1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=buttons)
