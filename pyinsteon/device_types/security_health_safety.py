"""Security, Heath and Safety device types."""
from ..events import HEARTBEAT_EVENT, LOW_BATTERY_EVENT, Event
from ..states import LOW_BATTERY_STATE, LIGHT_SENSOR_STATE
from ..states.on_off import LowBattery, OnOff
from . import BatteryDeviceBase, Device
from .commands import OFF_INBOUND, ON_INBOUND
from .on_off_controller_base import OnOffControllerBase
from .open_close_controller_base import NormallyOpenControllerBase, NormallyClosedControllerBase


class SecurityHealthSafety(Device):
    """Security, Health and Safety base device."""


class SecurityHealthSafety_DoorSensor(BatteryDeviceBase, OnOffControllerBase):
    """Door sensor model 2845-222 or similar."""

    def __init__(self, address, cat, subcat, firmware=0x00,
                 description='', model=''):
        """Init the SecurityHealthSafety_DoorSensor class."""
        super().__init__(address=address, cat=cat, subcat=subcat, firmware=firmware,
                         description=description, model=model, buttons=[1])

    def _register_states(self):
        """Register states for the Door Sensor."""
        super()._register_states()
        self._states[3] = LowBattery(name=LOW_BATTERY_STATE, address=self._address, group=3)
        self._states[3].add_handler(self._handlers[ON_INBOUND])
        self._states[3].add_handler(self._handlers[OFF_INBOUND])

        self._handlers[ON_INBOUND].subscribe(self._heartbeat_on_level_received)
        self._handlers[OFF_INBOUND].subscribe(self._heartbeat_off_received)

    def _register_events(self):
        """Register events for the Door Sensor."""
        self._events[LOW_BATTERY_EVENT] = Event(
            name=LOW_BATTERY_EVENT, address=self._address, group=3)
        self._events[LOW_BATTERY_EVENT].add_handler(self._handlers[ON_INBOUND])
        self._events[LOW_BATTERY_EVENT].add_handler(self._handlers[OFF_INBOUND])

        self._events[HEARTBEAT_EVENT] = Event(
            name=HEARTBEAT_EVENT, address=self._address, group=4)
        self._events[HEARTBEAT_EVENT].add_handler(self._handlers[ON_INBOUND])
        self._events[HEARTBEAT_EVENT].add_handler(self._handlers[OFF_INBOUND])

    def _heartbeat_on_level_received(self, on_level, group):
        """Receive a heartbeat signal as an ON command."""
        if group == 4:
            self._states[1].value = 0xff

    def _heartbeat_off_received(self, on_level, group):
        """Receive a heartbeat signal as an OFF command."""
        if group == 4:
            self._states[1].value = 0

    def _register_operating_flags(self):
        """Register operating flags for Door Sensor."""
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_ON, TWO_GROUPS_ON, LINK_TO_FF_GROUP,
                                      REPEAT_CLOSED_ON, REPEAT_OPEN_ON, CLEANUP_REPORT_ON,
                                      DATABASE_DELTA, STAY_AWAKE_ON)
        from ..extended_property import (BATTERY_LEVEL, SENSOR_STATUS, HEARBEAT_INTERVAL,
                                         BATTERY_LOW_LEVEL)

        super()._register_operating_flags()
        self._remove_operating_flag('bit0', 0)  # 01
        self._remove_operating_flag('bit1', 0)  # 02
        self._remove_operating_flag('bit3', 0)  # 02
        self._remove_operating_flag('bit4', 0)  # 10
        self._remove_operating_flag('bit5', 0)  # 20

        self._add_operating_flag(CLEANUP_REPORT_ON, 0, 1, 16, 17)
        self._add_operating_flag(TWO_GROUPS_ON, 0, 1, 4, 5)
        self._add_operating_flag(REPEAT_OPEN_ON, 0, 2, 0x10, 0x11)
        self._add_operating_flag(REPEAT_CLOSED_ON, 0, 3, 8, 9)
        self._add_operating_flag(LINK_TO_FF_GROUP, 0, 4, 6, 7)
        self._add_operating_flag(LED_ON, 0, 5, 2, 3)
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 7, 0, 1)

        self._add_operating_flag(STAY_AWAKE_ON, 0, 6, 18, 19)

        self._add_operating_flag(DATABASE_DELTA, 1, None, None, None)

        self._add_property(name=BATTERY_LEVEL, data_field=4, set_cmd=None)
        self._add_property(name=SENSOR_STATUS, data_field=5, set_cmd=None)
        self._add_property(name=HEARBEAT_INTERVAL, data_field=6, set_cmd=2)
        self._add_property(name=BATTERY_LOW_LEVEL, data_field=6, set_cmd=3)


class SecurityHealthSafety_OpenCloseSensor(BatteryDeviceBase, NormallyOpenControllerBase):
    """Normally Open sensor."""

    def _register_operating_flags(self):
        super()._register_operating_flags()
        from ..operating_flag import (PROGRAM_LOCK_ON, LED_ON, TWO_GROUPS_ON, LINK_TO_FF_GROUP,
                                      REPEAT_CLOSED_ON, REPEAT_OPEN_ON, CLEANUP_REPORT_ON,
                                      IGNORE_JUMPER_ON)
        from ..extended_property import LED_BRIGHTNESS
        self._add_property(name=LED_BRIGHTNESS, data_field=3, set_cmd=0x02)
        self._add_property(name=CLEANUP_REPORT_ON, data_field=6, set_cmd=0x05, bit=0)
        self._add_property(name=IGNORE_JUMPER_ON, data_field=6, set_cmd=0x05, bit=1)
        self._add_property(name=TWO_GROUPS_ON, data_field=6, set_cmd=0x05, bit=2)
        self._add_property(name=REPEAT_OPEN_ON, data_field=6, set_cmd=0x05, bit=3)
        self._add_property(name=REPEAT_CLOSED_ON, data_field=6, set_cmd=0x05, bit=4)
        self._add_property(name=LED_ON, data_field=6, set_cmd=0x05, bit=5)
        self._add_property(name=LINK_TO_FF_GROUP, data_field=6, set_cmd=0x05, bit=6)
        self._add_property(name=PROGRAM_LOCK_ON, data_field=6, set_cmd=0x05, bit=7)

class SecurityHealthSafety_MotionSensor(BatteryDeviceBase, OnOffControllerBase):
    """Motion Sensor."""

    def _register_states(self):
        """Register states for the Door Sensor."""
        super()._register_states()
        # This list state may be reversed where 0x11 means no light and 0x13 means light
        self._states[2] = OnOff(name=LIGHT_SENSOR_STATE, address=self._address, group=2)
        self._states[2].add_handler(self._handlers[ON_INBOUND])
        self._states[2].add_handler(self._handlers[OFF_INBOUND])

        self._states[3] = LowBattery(name=LOW_BATTERY_STATE, address=self._address, group=3)
        self._states[3].add_handler(self._handlers[ON_INBOUND])
        self._states[3].add_handler(self._handlers[OFF_INBOUND])

    def _register_operating_flags(self):
        super()._register_operating_flags()
        from ..operating_flag import (LED_ON, SEND_ON_ONLY, NIGHT_MODE_ONLY,
                                      MULTI_SEND_ON, SOFTWARE_SUPPORT_ON,
                                      HARDWARE_SEND_ON_ONLY, HARDWARE_NIGHT_MODE,
                                      HARDWARE_LED_OFF)
        from ..extended_property import (LED_BRIGHTNESS, MOTION_TIMEOUT, LIGHT_SENSITIVITY,
                                         HARDWARE_TIMEOUT, HARDWARE_LIGHT_SENSITIVITY,
                                         AMBIENT_LIGHT_INTENSITY, BATTERY_LEVEL)


        self._add_property(name=LED_BRIGHTNESS, data_field=3, set_cmd=0x02)
        self._add_property(name=MOTION_TIMEOUT, data_field=4, set_cmd=0x03)
        self._add_property(name=LIGHT_SENSITIVITY, data_field=5, set_cmd=0x04)

        self._add_property(name=SEND_ON_ONLY, data_field=6, set_cmd=0x05, bit=1)
        self._add_property(name=NIGHT_MODE_ONLY, data_field=6, set_cmd=0x05, bit=2)
        self._add_property(name=LED_ON, data_field=6, set_cmd=0x05, bit=3)
        self._add_property(name=MULTI_SEND_ON, data_field=6, set_cmd=0x05, bit=4)

        self._add_property(name=HARDWARE_TIMEOUT, data_field=7, set_cmd=None)
        self._add_property(name=HARDWARE_LIGHT_SENSITIVITY, data_field=8, set_cmd=None)

        self._add_property(name=SOFTWARE_SUPPORT_ON, data_field=9, set_cmd=None, bit=0)
        self._add_property(name=HARDWARE_SEND_ON_ONLY, data_field=9, set_cmd=None, bit=1)
        self._add_property(name=HARDWARE_NIGHT_MODE, data_field=9, set_cmd=None, bit=2)
        self._add_property(name=HARDWARE_LED_OFF, data_field=9, set_cmd=None, bit=3)

        self._add_property(name=AMBIENT_LIGHT_INTENSITY, data_field=11, set_cmd=None)
        self._add_property(name=BATTERY_LEVEL, data_field=12, set_cmd=None)
