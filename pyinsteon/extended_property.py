"""Representaton of an extended property of a device."""
from .device_flag import DeviceFlagBase
from .address import Address

RAMP_RATE = "ramp_rate"
X10_HOUSE = "x10_house"
X10_UNIT = "x10_unit"
LED_DIMMING = "led_dimming"
ON_LEVEL = "on_level"
AWAKE_INTERVAL = "awake_interval"
SLEEP_INTERVAL = "sleep_interval"
BROADCAST_NUMBER = "broadcast_number"
TRIGGER_GROUP_BIT_MASK = "trigger_group_bit_mask"
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


class ExtendedProperty(DeviceFlagBase):
    """Representaton of an extended property of a device."""

    def __init__(self, address, name, flag_type: type):
        """Init the ExtendedProperty class."""
        self._address = Address(address)
        topic = "{}.property.{}".format(self._address.id, name)
        super().__init__(topic, name, flag_type)
