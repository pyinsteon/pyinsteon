"""Representaton of an extended property of a device."""
from .device_flag import DeviceFlagBase

RAMP_RATE = 'ramp_rate'
X10_HOUSE = 'x10_house'
X10_UNIT = 'x10_unit'
LED_DIMMING = 'led_dimming'
ON_LEVEL = 'on_level'
AWAKE_INTERVAL = 'awake_interval'
SLEEP_INTERVAL = 'sleep_interval'
BROADCAST_NUMBER = 'broadcast_number'
TRIGGER_GROUP_BIT_MASK = 'trigger_group_bit_mask'
LSB_OF_SLEEP_INTERVAL = 'lsb_of_sleep_interval'
APP_RETRIES = 'app_retries'
CONFIG = 'config'
BATTERY_LEVEL = 'config_battery_level'
DATABASE_DELTA = 'database_delta'


class ExtendedProperty(DeviceFlagBase):
    """Representaton of an extended property of a device."""
