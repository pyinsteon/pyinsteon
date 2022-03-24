"""Security, Heath and Safety device types."""
from ..config import (
    AMBIENT_LIGHT_INTENSITY,
    BATTERY_LEVEL,
    BATTERY_LOW_LEVEL,
    CLEANUP_REPORT_ON,
    DATABASE_DELTA,
    HARDWARE_LED_OFF,
    HARDWARE_LIGHT_SENSITIVITY,
    HARDWARE_NIGHT_MODE,
    HARDWARE_SEND_ON_ONLY,
    HARDWARE_TIMEOUT,
    HEARBEAT_INTERVAL,
    HEART_BEAT_ON,
    IGNORE_JUMPER_ON,
    LED_BLINK_ON_TX_ON,
    LED_BRIGHTNESS,
    LED_OFF,
    LED_ON,
    LIGHT_SENSITIVITY,
    LINK_TO_FF_GROUP,
    MOTION_TIMEOUT,
    MULTI_SEND_ON,
    NIGHT_MODE_ONLY,
    PROGRAM_LOCK_ON,
    REPEAT_CLOSED_ON,
    REPEAT_OPEN_ON,
    SEND_ON_ONLY,
    SENSOR_STATUS,
    SOFTWARE_SUPPORT_ON,
    STAY_AWAKE_ON,
    TWO_GROUPS_ON,
)
from ..default_link import DefaultLink
from ..events import (
    ALL_CLEAR_EVENT,
    CLOSE_EVENT,
    CO_DETECTED_EVENT,
    DARK_DETECTED_EVENT,
    HEARTBEAT_EVENT,
    LEAK_DRY_EVENT,
    LEAK_WET_EVENT,
    LIGHT_DETECTED_EVENT,
    LOW_BATTERY_EVENT,
    MOTION_DETECTED_EVENT,
    MOTION_TIMEOUT_EVENT,
    NEW_DETECTED_EVENT,
    OPEN_EVENT,
    SENSOR_MALFUNCTION_EVENT,
    SMOKE_DETECTED_EVENT,
    TEST_DETECTED_EVENT,
    Event,
    HeartbeatEvent,
    LowBatteryEvent,
    WetDryEvent,
)
from ..groups import (
    CO_SENSOR,
    DOOR_SENSOR,
    HEARTBEAT,
    LEAK_SENSOR_DRY,
    LEAK_SENSOR_WET,
    LIGHT_SENSOR,
    LOW_BATTERY,
    MOTION_SENSOR,
    NEW_SENSOR,
    SENSOR_MALFUNCTION,
    SMOKE_SENSOR,
    TEST_SENSOR,
)
from ..groups.on_off import Heartbeat, LowBattery, OnOff
from ..groups.wet_dry import Dry, Wet
from ..handlers.from_device.on_level import OnLevelInbound
from ..managers.heartbeat_manager import HeartbeatManager
from ..managers.low_batter_manager import LowBatteryManager
from ..managers.on_level_manager import OnLevelManager
from ..managers.wet_dry_manager import WetDryManager
from .battery_base import BatteryDeviceBase
from .device_base import Device
from .on_off_controller_base import OnOffControllerBase
from .open_close_controller_base import NormallyOpenControllerBase


class SecurityHealthSafety(Device):
    """Security, Health and Safety base device."""


class SecurityHealthSafety_DoorSensor(BatteryDeviceBase, OnOffControllerBase):
    """Door sensor model 2845-222 or similar."""

    DOOR_GROUP = 1
    LOW_BATTERY_GROUP = 3
    HEARTBEAT_GROUP = 4

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the SecurityHealthSafety_DoorSensor class."""
        buttons = {1: DOOR_SENSOR}
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
            on_event_name=OPEN_EVENT,
            off_event_name=CLOSE_EVENT,
        )

    def _register_handlers_and_managers(self):
        """Register handlers and managers."""
        super()._register_handlers_and_managers()
        self._low_battery_manger = LowBatteryManager(
            self._address, self.LOW_BATTERY_GROUP
        )
        self._heartbeat_manger = HeartbeatManager(self._address, self.HEARTBEAT_GROUP)

    def _register_groups(self):
        """Register groups for the Door Sensor."""
        super()._register_groups()
        self._groups[self.LOW_BATTERY_GROUP] = LowBattery(
            name=LOW_BATTERY, address=self._address, group=self.LOW_BATTERY_GROUP
        )

        self._groups[self.HEARTBEAT_GROUP] = Heartbeat(
            name=HEARTBEAT,
            address=self._address,
            group=self.HEARTBEAT_GROUP,
            default=False,
        )

    def _register_events(self):
        """Register events for the Door Sensor."""
        super()._register_events()
        self._events[LOW_BATTERY_EVENT] = LowBatteryEvent(
            name=LOW_BATTERY_EVENT, address=self._address, group=self.LOW_BATTERY_GROUP
        )
        self._events[HEARTBEAT_EVENT] = HeartbeatEvent(
            name=HEARTBEAT_EVENT, address=self._address, group=self.HEARTBEAT_GROUP
        )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._low_battery_manger.subscribe(
            self._groups[self.LOW_BATTERY_GROUP].set_value
        )
        self._heartbeat_manger.subscribe_on(self._groups[self.DOOR_GROUP].set_value)
        self._heartbeat_manger.subscribe_off(self._groups[self.DOOR_GROUP].set_value)
        self._heartbeat_manger.subscribe(self._groups[self.HEARTBEAT_GROUP].set_value)
        self._low_battery_manger.subscribe_low_battery_event(
            self._events[LOW_BATTERY_EVENT].trigger
        )
        self._heartbeat_manger.subscribe(self._events[HEARTBEAT_EVENT].trigger)

    def _register_op_flags_and_props(self):
        """Register operating flags for Door Sensor."""
        super()._register_op_flags_and_props()

        self._add_operating_flag(CLEANUP_REPORT_ON, 0, 1, 16, 17)
        self._add_operating_flag(TWO_GROUPS_ON, 0, 1, 4, 5)
        self._add_operating_flag(REPEAT_OPEN_ON, 0, 2, 0x10, 0x11)
        self._add_operating_flag(REPEAT_CLOSED_ON, 0, 3, 8, 9)
        self._add_operating_flag(LINK_TO_FF_GROUP, 0, 4, 6, 7)
        self._add_operating_flag(LED_OFF, 0, 5, 2, 3)
        self._add_operating_flag(PROGRAM_LOCK_ON, 0, 7, 0, 1)

        self._add_operating_flag(STAY_AWAKE_ON, 0, 6, 18, 19)

        self._add_operating_flag(DATABASE_DELTA, 1, None, None, None)

        self._add_property(name=BATTERY_LEVEL, data_field=4, set_cmd=None)
        self._add_property(name=SENSOR_STATUS, data_field=5, set_cmd=None)
        self._add_property(name=HEARBEAT_INTERVAL, data_field=6, set_cmd=2)
        self._add_property(name=BATTERY_LOW_LEVEL, data_field=6, set_cmd=3)

    def _register_default_links(self):
        super()._register_default_links()
        link_battery = DefaultLink(
            is_controller=True,
            group=self.LOW_BATTERY_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.LOW_BATTERY_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_heartbeat = DefaultLink(
            is_controller=True,
            group=self.HEARTBEAT_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.HEARTBEAT_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        self._default_links.append(link_battery)
        self._default_links.append(link_heartbeat)


class SecurityHealthSafety_OpenCloseSensor(
    BatteryDeviceBase, NormallyOpenControllerBase
):
    """Normally Open sensor."""

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
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

    MOTION_GROUP = 1
    LIGHT_GROUP = 2
    LOW_BATTERY_GROUP = 3

    def __init__(self, address, cat, subcat, firmware=0x00, description="", model=""):
        """Init the SecurityHealthSafety_DoorSensor class."""
        buttons = {1: MOTION_SENSOR}
        self._light_manager = OnLevelManager(address, self.LIGHT_GROUP)
        self._low_battery_manager = LowBatteryManager(address, self.LOW_BATTERY_GROUP)
        super().__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            description=description,
            model=model,
            buttons=buttons,
            on_event_name=MOTION_DETECTED_EVENT,
            off_event_name=MOTION_TIMEOUT_EVENT,
        )

    def _register_groups(self):
        """Register groups for the Door Sensor."""
        super()._register_groups()
        # This list state may be reversed where 0x11 means no light and 0x13 means light
        self._groups[self.LIGHT_GROUP] = OnOff(
            LIGHT_SENSOR, self._address, self.LIGHT_GROUP
        )
        self._groups[self.LOW_BATTERY_GROUP] = LowBattery(
            LOW_BATTERY, self._address, self.LOW_BATTERY_GROUP
        )

    def _register_events(self):
        """Register events for the Door Sensor."""
        super()._register_events()
        self._events[self.LIGHT_GROUP] = {}
        self._events[self.LIGHT_GROUP][LIGHT_DETECTED_EVENT] = Event(
            LIGHT_DETECTED_EVENT, self._address, self.LIGHT_GROUP
        )
        self._events[self.LIGHT_GROUP][DARK_DETECTED_EVENT] = Event(
            DARK_DETECTED_EVENT, self._address, self.LIGHT_GROUP
        )
        self._events[self.LOW_BATTERY_GROUP] = {}
        self._events[self.LOW_BATTERY_GROUP][LOW_BATTERY_EVENT] = LowBatteryEvent(
            LOW_BATTERY_EVENT, self._address, self.LOW_BATTERY_GROUP
        )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()
        self._light_manager.subscribe(self._groups[self.LIGHT_GROUP].set_value)
        self._low_battery_manager.subscribe(
            self._groups[self.LOW_BATTERY_GROUP].set_value
        )

        self._light_manager.subscribe_on(
            self._events[self.LIGHT_GROUP][LIGHT_DETECTED_EVENT].trigger
        )
        self._light_manager.subscribe_off(
            self._events[self.LIGHT_GROUP][DARK_DETECTED_EVENT].trigger
        )
        self._low_battery_manager.subscribe_low_battery_event(
            self._events[self.LOW_BATTERY_GROUP][LOW_BATTERY_EVENT].trigger
        )

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
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
        self._add_property(
            name=HARDWARE_SEND_ON_ONLY, data_field=9, set_cmd=None, bit=1
        )
        self._add_property(name=HARDWARE_NIGHT_MODE, data_field=9, set_cmd=None, bit=2)
        self._add_property(name=HARDWARE_LED_OFF, data_field=9, set_cmd=None, bit=3)

        self._add_property(name=AMBIENT_LIGHT_INTENSITY, data_field=11, set_cmd=None)
        self._add_property(name=BATTERY_LEVEL, data_field=12, set_cmd=None)

    def _register_default_links(self):
        super()._register_default_links()
        link_light = DefaultLink(
            is_controller=True,
            group=self.LIGHT_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.LIGHT_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_battery = DefaultLink(
            is_controller=True,
            group=self.LOW_BATTERY_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.LOW_BATTERY_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        self._default_links.append(link_light)
        self._default_links.append(link_battery)


class SecurityHealthSafety_LeakSensor(BatteryDeviceBase, Device):
    """Leak Sensor device."""

    DRY_GROUP = 1
    WET_GROUP = 2
    HEARTBEAT_GROUP = 4
    WET_DRY_MANGER = "manager"

    def _register_handlers_and_managers(self):
        """Regsister handlers and managers for the Leak Sensor."""
        super()._register_handlers_and_managers()
        self._managers[self.WET_DRY_MANGER] = WetDryManager(self._address)
        self._managers[self.HEARTBEAT_GROUP] = HeartbeatManager(
            self._address, self.HEARTBEAT_GROUP
        )

    def _register_groups(self):
        """Register groups for the Door Sensor."""
        # Group 1 is the Dry state. This uses the following definition:
        #   Dry = Closed
        #   Wet = Open
        # When an ON message (0x11) is received for group 1 the sensor is dry.
        # When an ON message (0x11) is received for group 2 the sensor is wet.
        # Dry state is handled via the Dry event below

        self._groups[self.DRY_GROUP] = Dry(
            LEAK_SENSOR_DRY, self._address, self.DRY_GROUP
        )
        self._groups[self.WET_GROUP] = Wet(
            LEAK_SENSOR_WET, self._address, self.WET_GROUP
        )
        self._groups[self.HEARTBEAT_GROUP] = Heartbeat(
            HEARTBEAT, self._address, self.HEARTBEAT_GROUP, default=False
        )

    def _register_events(self):
        """Register events for the Door Sensor."""
        self._events[LEAK_DRY_EVENT] = WetDryEvent(
            LEAK_DRY_EVENT, self._address, self.DRY_GROUP
        )
        self._events[LEAK_WET_EVENT] = WetDryEvent(
            LEAK_WET_EVENT, self._address, self.WET_GROUP
        )
        self._events[HEARTBEAT_EVENT] = HeartbeatEvent(
            HEARTBEAT_EVENT, self._address, self.HEARTBEAT_GROUP
        )

    def _subscribe_to_handelers_and_managers(self):
        """Subscribe to handlers and managers."""
        super()._subscribe_to_handelers_and_managers()
        dry_group = self._groups[self.DRY_GROUP]
        wet_group = self._groups[self.WET_GROUP]
        dry_event = self._events[LEAK_DRY_EVENT]
        wet_event = self._events[LEAK_WET_EVENT]
        hb_event = self._events[HEARTBEAT_EVENT]
        wet_dry_mgr = self._managers[self.WET_DRY_MANGER]
        hb_mgr = self._managers[self.HEARTBEAT_GROUP]

        wet_dry_mgr.subscribe(dry_group.set_value)
        wet_dry_mgr.subscribe(wet_group.set_value)

        wet_dry_mgr.subscribe_dry(dry_event.trigger)
        wet_dry_mgr.subscribe_wet(wet_event.trigger)

        hb_mgr.subscribe(hb_event.trigger)
        hb_mgr.subscribe_on(self._heartbeat_dry)
        hb_mgr.subscribe_off(self._heartbeat_wet)

    def _heartbeat_dry(self, on_level):
        """Receive heartbeat on/off message and create wet/dry status."""
        self._groups[self.DRY_GROUP].value = True
        self._groups[self.WET_GROUP].value = False
        self._events[LEAK_DRY_EVENT].trigger(on_level)

    def _heartbeat_wet(self, on_level):
        """Receive heartbeat on/off message and create wet/dry status."""
        self._groups[self.DRY_GROUP].value = False
        self._groups[self.WET_GROUP].value = True
        self._events[LEAK_WET_EVENT].trigger(on_level)

    def _register_op_flags_and_props(self):
        # bit 0 = Cleanup Report
        # bit 1 = Don’t Read the Jumper
        # bit 2 = 2 Groups
        # bit 3 = Repeat Open
        # bit 4 = Repeat Closed
        # bit 5 = LED On/Off
        # bit 6 = Link to FF Group
        # bit 7 = Programming Lock
        # (0x4F is the default Config Byte)

        self._add_property(name=LED_BRIGHTNESS, data_field=3, set_cmd=2)

        self._add_property(name=CLEANUP_REPORT_ON, data_field=6, set_cmd=5, bit=0)
        self._add_property(name=IGNORE_JUMPER_ON, data_field=6, set_cmd=5, bit=1)
        self._add_property(name=TWO_GROUPS_ON, data_field=6, set_cmd=5, bit=2)
        self._add_property(name=REPEAT_OPEN_ON, data_field=6, set_cmd=5, bit=3)
        self._add_property(name=REPEAT_CLOSED_ON, data_field=6, set_cmd=5, bit=4)
        self._add_property(name=LED_ON, data_field=6, set_cmd=5, bit=5)
        self._add_property(name=LINK_TO_FF_GROUP, data_field=6, set_cmd=5, bit=6)
        self._add_property(name=PROGRAM_LOCK_ON, data_field=6, set_cmd=5, bit=7)

    def _register_default_links(self):
        super()._register_default_links()
        link_dry = DefaultLink(
            is_controller=True,
            group=self.DRY_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.DRY_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_wet = DefaultLink(
            is_controller=True,
            group=self.WET_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.WET_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_heartbeat = DefaultLink(
            is_controller=True,
            group=self.HEARTBEAT_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.HEARTBEAT_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        self._default_links.append(link_dry)
        self._default_links.append(link_wet)
        self._default_links.append(link_heartbeat)


class SecurityHealthSafety_Smokebridge(Device):
    """Smokebridge device."""

    SMOKE_DETECTED_GROUP = 1
    CO_DETECTED_GROUP = 2
    TEST_DETECTED_GROUP = 3
    NEW_DETECTED_GROUP = 4
    ALL_CLEAR_GROUP = 5
    LOW_BATTERY_GROUP = 6
    SENSOR_MALFUNCTION_GROUP = 7
    HEARTBEAT_GROUP = 0x0A

    def _register_handlers_and_managers(self):
        super()._register_handlers_and_managers()
        self._handlers[self.SMOKE_DETECTED_GROUP] = OnLevelInbound(
            self._address, self.SMOKE_DETECTED_GROUP
        )
        self._handlers[self.CO_DETECTED_GROUP] = OnLevelInbound(
            self._address, self.CO_DETECTED_GROUP
        )
        self._handlers[self.TEST_DETECTED_GROUP] = OnLevelInbound(
            self._address, self.TEST_DETECTED_GROUP
        )
        self._handlers[self.NEW_DETECTED_GROUP] = OnLevelInbound(
            self._address, self.NEW_DETECTED_GROUP
        )
        self._handlers[self.SENSOR_MALFUNCTION_GROUP] = OnLevelInbound(
            self._address, self.SENSOR_MALFUNCTION_GROUP
        )

        self._handlers[self.ALL_CLEAR_GROUP] = OnLevelInbound(
            self._address, self.ALL_CLEAR_GROUP
        )
        self._managers[self.LOW_BATTERY_GROUP] = LowBatteryManager(
            self._address, self.LOW_BATTERY_GROUP
        )
        self._managers[self.HEARTBEAT_GROUP] = HeartbeatManager(
            self._address, self.HEARTBEAT_GROUP
        )

    def _register_groups(self):
        super()._register_groups()
        self._groups[self.SMOKE_DETECTED_GROUP] = OnOff(
            SMOKE_SENSOR, self._address, self.SMOKE_DETECTED_GROUP
        )
        self._groups[self.CO_DETECTED_GROUP] = OnOff(
            CO_SENSOR, self._address, self.CO_DETECTED_GROUP
        )
        self._groups[self.TEST_DETECTED_GROUP] = OnOff(
            TEST_SENSOR, self._address, self.TEST_DETECTED_GROUP
        )
        self._groups[self.NEW_DETECTED_GROUP] = OnOff(
            NEW_SENSOR, self._address, self.NEW_DETECTED_GROUP
        )
        self._groups[self.LOW_BATTERY_GROUP] = LowBattery(
            LOW_BATTERY, self._address, self.LOW_BATTERY_GROUP
        )
        self._groups[self.SENSOR_MALFUNCTION_GROUP] = OnOff(
            SENSOR_MALFUNCTION, self._address, self.SENSOR_MALFUNCTION_GROUP
        )
        self._groups[self.HEARTBEAT_GROUP] = Heartbeat(
            HEARTBEAT, self._address, self.HEARTBEAT_GROUP, default=False
        )

    def _register_events(self):
        super()._register_events()
        self._events[SMOKE_DETECTED_EVENT] = Event(
            SMOKE_DETECTED_EVENT, self._address, self.SMOKE_DETECTED_GROUP
        )
        self._events[CO_DETECTED_EVENT] = Event(
            CO_DETECTED_EVENT, self._address, self.CO_DETECTED_GROUP
        )
        self._events[TEST_DETECTED_EVENT] = Event(
            TEST_DETECTED_EVENT, self._address, self.TEST_DETECTED_GROUP
        )
        self._events[NEW_DETECTED_EVENT] = Event(
            NEW_DETECTED_EVENT, self._address, self.NEW_DETECTED_GROUP
        )
        self._events[ALL_CLEAR_EVENT] = Event(
            ALL_CLEAR_EVENT, self._address, self.ALL_CLEAR_GROUP
        )
        self._events[LOW_BATTERY_EVENT] = LowBatteryEvent(
            LOW_BATTERY_EVENT, self._address, self.LOW_BATTERY_GROUP
        )
        self._events[SENSOR_MALFUNCTION_EVENT] = Event(
            SENSOR_MALFUNCTION_EVENT, self._address, self.SENSOR_MALFUNCTION_GROUP
        )
        self._events[HEARTBEAT_EVENT] = HeartbeatEvent(
            HEARTBEAT_EVENT, self._address, self.HEARTBEAT_GROUP
        )

    def _subscribe_to_handelers_and_managers(self):
        super()._subscribe_to_handelers_and_managers()

        self._handlers[self.SMOKE_DETECTED_GROUP].subscribe(
            self._groups[self.SMOKE_DETECTED_GROUP].set_value
        )
        self._handlers[self.SMOKE_DETECTED_GROUP].subscribe(
            self._events[SMOKE_DETECTED_EVENT].trigger
        )

        self._handlers[self.CO_DETECTED_GROUP].subscribe(
            self._groups[self.CO_DETECTED_GROUP].set_value
        )
        self._handlers[self.CO_DETECTED_GROUP].subscribe(
            self._events[CO_DETECTED_EVENT].trigger
        )

        self._handlers[self.TEST_DETECTED_GROUP].subscribe(
            self._groups[self.TEST_DETECTED_GROUP].set_value
        )
        self._handlers[self.TEST_DETECTED_GROUP].subscribe(
            self._events[TEST_DETECTED_EVENT].trigger
        )

        self._handlers[self.NEW_DETECTED_GROUP].subscribe(
            self._groups[self.NEW_DETECTED_GROUP].set_value
        )
        self._handlers[self.NEW_DETECTED_GROUP].subscribe(
            self._events[NEW_DETECTED_EVENT].trigger
        )

        self._handlers[self.SENSOR_MALFUNCTION_GROUP].subscribe(
            self._groups[self.SENSOR_MALFUNCTION_GROUP].set_value
        )
        self._handlers[self.SENSOR_MALFUNCTION_GROUP].subscribe(
            self._events[SENSOR_MALFUNCTION_EVENT].trigger
        )

        self._handlers[self.ALL_CLEAR_GROUP].subscribe(self._all_clear_received)

    def _all_clear_received(self, on_level):
        """All-Clear message received."""
        if self._groups[self.SMOKE_DETECTED_GROUP].value:
            self._groups[self.SMOKE_DETECTED_GROUP].set_value(0)
        if self._groups[self.CO_DETECTED_GROUP].value:
            self._groups[self.CO_DETECTED_GROUP].set_value(0)
        if self._groups[self.TEST_DETECTED_GROUP].value:
            self._groups[self.TEST_DETECTED_GROUP].set_value(0)
        if self._groups[self.NEW_DETECTED_GROUP].value:
            self._groups[self.NEW_DETECTED_GROUP].set_value(0)
        if self._groups[self.SENSOR_MALFUNCTION_GROUP].value:
            self._groups[self.SENSOR_MALFUNCTION_GROUP].set_value(0)

    def _register_op_flags_and_props(self):
        super()._register_op_flags_and_props()
        self._add_operating_flag(
            name=PROGRAM_LOCK_ON, group=0, bit=0, set_cmd=0, unset_cmd=1
        )
        self._add_operating_flag(
            name=LED_BLINK_ON_TX_ON, group=0, bit=1, set_cmd=2, unset_cmd=3
        )
        self._add_operating_flag(name=LED_OFF, group=0, bit=4, set_cmd=8, unset_cmd=9)
        self._add_operating_flag(
            name=HEART_BEAT_ON, group=0, bit=5, set_cmd=6, unset_cmd=7
        )
        self._add_operating_flag(
            name=CLEANUP_REPORT_ON, group=0, bit=6, set_cmd=0x0B, unset_cmd=0x0A
        )

    def _register_default_links(self):
        super()._register_default_links()

        link_smoke = DefaultLink(
            is_controller=True,
            group=self.SMOKE_DETECTED_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.SMOKE_DETECTED_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_co = DefaultLink(
            is_controller=True,
            group=self.CO_DETECTED_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.CO_DETECTED_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_test = DefaultLink(
            is_controller=True,
            group=self.TEST_DETECTED_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.TEST_DETECTED_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_new = DefaultLink(
            is_controller=True,
            group=self.NEW_DETECTED_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.NEW_DETECTED_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_clear = DefaultLink(
            is_controller=True,
            group=self.ALL_CLEAR_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.ALL_CLEAR_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_battery = DefaultLink(
            is_controller=True,
            group=self.LOW_BATTERY_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.LOW_BATTERY_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_malfunction = DefaultLink(
            is_controller=True,
            group=self.SENSOR_MALFUNCTION_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.SENSOR_MALFUNCTION_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )
        link_heartbeat = DefaultLink(
            is_controller=True,
            group=self.HEARTBEAT_GROUP,
            dev_data1=255,
            dev_data2=28,
            dev_data3=self.HEARTBEAT_GROUP,
            modem_data1=0,
            modem_data2=0,
            modem_data3=0,
        )

        self._default_links.append(link_smoke)
        self._default_links.append(link_co)
        self._default_links.append(link_test)
        self._default_links.append(link_new)
        self._default_links.append(link_clear)
        self._default_links.append(link_battery)
        self._default_links.append(link_malfunction)
        self._default_links.append(link_heartbeat)
