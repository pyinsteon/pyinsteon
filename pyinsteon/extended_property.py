"""Representaton of an extended property of a device."""
from .address import Address
from .device_flag import DeviceFlagBase

RAMP_RATE = "ramp_rate"
X10_HOUSE = "x10_house"
X10_UNIT = "x10_unit"
LED_DIMMING = "led_dimming"
ON_LEVEL = "on_level"
AWAKE_INTERVAL = "awake_interval"
SLEEP_INTERVAL = "sleep_interval"
BROADCAST_NUMBER = "broadcast_number"
TRIGGER_GROUP_MASK = "trigger_group_mask"
LSB_OF_SLEEP_INTERVAL = "lsb_of_sleep_interval"
APP_RETRIES = "app_retries"
CONFIG = "config"
BATTERY_LEVEL = "battery_level"
DATABASE_DELTA = "database_delta"
SENSOR_STATUS = "sensor_status"
HEARBEAT_INTERVAL = "heartbeat_interval"
BATTERY_LOW_LEVEL = "battery_low_level"
LED_BRIGHTNESS = "led_brightness"
MOTION_TIMEOUT = "motion_timeout"
LIGHT_SENSITIVITY = "light_sensitivity"
HARDWARE_TIMEOUT = "hardware_timeout"
HARDWARE_LIGHT_SENSITIVITY = "hardware_light_sensitivity"
AMBIENT_LIGHT_INTENSITY = "ambient_light_intensity"
DELAY = "delay"
PRESCALER = "prescaler"
DURATION_HIGH = "duration_high"
DURATION_LOW = "duration_low"
ON_MASK = "on_mask"
OFF_MASK = "off_mask"
NON_TOGGLE_MASK = "non_toggle_mask"
NON_TOGGLE_ON_OFF_MASK = "non_toggle_on_off_mask"
BACKLIGHT = "backlight"
CHANGE_DELAY = "change_delay"
MASTER = "master"
HUMIDITY_HIGH = "humidity_high"
HUMIDITY_LOW = "humidity_low"
TEMP_OFFSET = "temp_offset"
TEMP_OFFSET_EXTERNAL = "temp_offset_external"
HUMIDITY_OFFSET = "humidity_offset"


class ExtendedProperty(DeviceFlagBase):
    """Representation of an extended property of a device."""

    def __init__(
        self, address, name, flag_type: type, is_reversed=False, is_read_only=False
    ):
        """Init the ExtendedProperty class."""
        self._address = Address(address)
        topic = "{}.property.{}".format(self._address.id, name)
        super().__init__(topic, name, flag_type, is_reversed, is_read_only)
