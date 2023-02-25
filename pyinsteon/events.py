"""Event class used to trigger event actions to subscribers.

Events include device triggered actions such as:
    - ON
    - OFF
    - FAST ON
    - FAST OFF

Subscribers to Event use the following interface:
    subscriber(name, address)
Where name is the name of the event and address is the address of the device
triggering the event.
"""
from .address import Address
from .subscriber_base import SubscriberBase

ON_EVENT = "on_event"
ON_FAST_EVENT = "on_fast_event"
OFF_EVENT = "off_event"
OFF_FAST_EVENT = "off_fast_event"
LOW_BATTERY_EVENT = "low_battery_event"
HEARTBEAT_EVENT = "heartbeat_event"
OPEN_EVENT = "open_event"
CLOSE_EVENT = "close_event"
LEAK_DRY_EVENT = "leak_dry_event"
LEAK_WET_EVENT = "leak_wet_event"
MOTION_DETECTED_EVENT = "motion_detected_event"
MOTION_TIMEOUT_EVENT = "motion_timeout_event"
LIGHT_DETECTED_EVENT = "light_detected_event"
DARK_DETECTED_EVENT = "dark_detected_event"
SMOKE_DETECTED_EVENT = "smoke_detected_event"
CO_DETECTED_EVENT = "co_detected_event"
TEST_DETECTED_EVENT = "test_detected_event"
NEW_DETECTED_EVENT = "new_detected_event"
LOW_BATTERY_EVENT = "low_battery_event"
LOW_BATTERY_CLEARED_EVENT = "low_battery_cleared_event"
SENSOR_MALFUNCTION_EVENT = "sensor_malfunction_event"
ALL_CLEAR_EVENT = "all_clear_event"


ALT_MOTION_OFF_EVENT = "alt_motion_off"
ALT_LIGHT_OFF_EVENT = "alt_light_off"
HOT_EVENT = "hot"
NOT_HOT_EVENT = "not_hot"
COLD_EVENT = "cold"
NOT_COLD_EVENT = "not_cold"
ALT_HOT_OFF_EVENT = "alt_hot_off"
ALT_COLD_OFF_EVENT = "alt_cold_off"
ALT_HEARTBEAT_EVENT = "alt_heartbeat"
MOTION_OFF_EVENT = "motion_off"
MOTION_DISABLED_EVENT = "motion_disabled"
MOTION_ENABLED_EVENT = "motion_enabled"
ALT_MOTION_DISABLED_EVENT = "alt_motion_disabled"
SENSOR_MOVED_EVENT = "sensor_moved"
TAMPER_EVENT = "tamper"
VERY_HOT_EVENT = "very_hot"
NOT_VERY_HOT_EVENT = "not_very_hot"
VERY_COLD_EVENT = "very_cold"
NOT_VERY_COLD_EVENT = "not_very_cold"
TEMP_CHANGED_EVENT = "temp_changed"
LIGHT_CHANGED_EVENT = "light_changed"


class Event(SubscriberBase):
    """Event class to manage triggering of events.

    Subscribers to Event use the following interface:

        subscriber(name, address, group)

    Where name is the name of the event and address is the address of the device
    triggering the event.
    """

    def __init__(self, name: str, address: Address, group=0, button=""):
        """Init the Event class."""
        self._address = address  # Address(address)
        self._group = group
        self._name = name
        self._button = button
        topic = f"event_{self._address.id}_{group}_{name}"
        super().__init__(subscriber_topic=topic)

    @property
    def address(self):
        """Address of the device sending the event."""
        return self._address

    @property
    def group(self):
        """Group number of the event."""
        return self._group

    @property
    def name(self):
        """Name of the event."""
        return self._name

    @property
    def button(self):
        """Return the button name."""
        return self._button

    def trigger(self, on_level):
        """Trigger the event."""
        self._call_subscribers(
            name=self._name,
            address=self._address.id,
            group=self._group,
            button=self._button,
        )


class LowBatteryEvent(Event):
    """Low battery event."""

    # pylint: disable=arguments-renamed
    def trigger(self, low_battery):
        """Trigger the event."""
        self._call_subscribers(
            name=self._name, address=self._address.id, group=self._group
        )


class HeartbeatEvent(Event):
    """Heartbeat event."""

    # pylint: disable=arguments-renamed
    def trigger(self, heartbeat):
        """Trigger the event."""
        self._call_subscribers(
            name=self._name, address=self._address.id, group=self._group
        )


class WetDryEvent(Event):
    """We or Dry event."""

    # pylint: disable=arguments-renamed
    def trigger(self, dry):
        """Trigger the event."""
        self._call_subscribers(
            name=self._name, address=self._address.id, group=self._group
        )
