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
        super().__init__(address, cat, subcat, firmware, description, model, buttons=5)


class GeneralController_RemoteLinc(BatteryDeviceBase, VariableControllerBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        self._button_names = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F'}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=6)

    def _register_operating_flags(self):
        from ..operating_flag import (STAY_AWAKE_ON)
        super()._register_operating_flags()
        self._remove_operating_flag('bit3', 0)
        self._add_operating_flag(STAY_AWAKE_ON, 0, 3, 6, 7)


class GeneralController_MiniRemoteBase(BatteryDeviceBase, VariableControllerBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model='', buttons=1):
        """Init the GeneralController_MiniRemoteBase class."""
        super().__init__(address, cat, subcat, firmware, description, model, buttons)
        self._database_delta = 0


    def _register_operating_flags(self):
        from ..operating_flag import (PROGRAM_LOCK_ON, STAY_AWAKE_ON, ON_ONLY_ON,
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
        self._add_operating_flag(ON_ONLY_ON, 0, 4, 8, 9)
        self._add_operating_flag(GROUPED_ON, 0, 6, 0x0e, 0x0f)


class GeneralController_MiniRemote_Switch(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device with a single button."""

    def __init__(self, address, cat, subcat, firmware=0x00, description='', model=''):
        """Init the GeneralController_MiniRemote_Switch class."""
        super().__init__(address, cat, subcat, firmware, description, model, buttons=1)


class GeneralController_MiniRemote_4(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        self._button_names = {1: 'A', 2: 'B', 3: 'C', 4: 'D'}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=4)


class GeneralController_MiniRemote_8(GeneralController_MiniRemoteBase):
    """RemoteLinc 2440 device."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        self._button_names = {1: 'B', 2: 'A', 3: 'D', 4: 'C',
                              5: 'F', 6: 'E', 7: 'H', 8: 'G'}
        super().__init__(address, cat, subcat, firmware, description, model, buttons=6)
