"""Device configuration settings."""

from ..constants import ToggleMode

# Operating Flags
PROGRAM_LOCK_ON = "program_lock_on"
BUTTON_LOCK_ON = "button_lock_on"
LED_ON = "led_on"
LED_OFF = "led_off"
KEY_BEEP_ON = "key_beep_on"
STAY_AWAKE_ON = "stay_awake_on"
LISTEN_ONLY_ON = "listen_only_on"
HEART_BEAT_ON = "heart_beat_on"
HEART_BEAT_OFF = "heart_beat_off"
SEND_ON_ONLY = "send_on_only_on"
GROUPED_ON = "grouped_on"
TWO_GROUPS_ON = "two_groups_on"
RESUME_DIM_ON = "resume_dim_on"
RF_DISABLE_ON = "rf_disable_on"
POWERLINE_DISABLE_ON = "powerline_disable_on"
TEND_ON = "tend_on"
X10_OFF = "x10_off"
CLEANUP_REPORT_ON = "cleanup_report_on"
CLEANUP_REPORT_OFF = "cleanup_report_off"
DETACH_LOAD_ON = "detach_load_on"
SMART_HOPS_ON = "smart_hops_on"
LED_BLINK_ON_ERROR_ON = "blink_on_error_on"
LED_BLINK_ON_ERROR_OFF = "blink_on_error_off"
LED_BLINK_ON_TX_ON = "blink_on_tx_on"
REPEAT_OPEN_ON = "repeat_open_on"
REPEAT_CLOSED_ON = "repeat_closed_on"
LINK_TO_FF_GROUP = "link_to_ff_group"
LOAD_SENSE_ON = "load_sense_on"
LOAD_SENSE_2_ON = "load_sense_2_on"
IGNORE_JUMPER_ON = "ignore_jumper_on"
NIGHT_MODE_ONLY = "night_mode_only"
MULTI_SEND_ON = "multi_send_on"
SOFTWARE_SUPPORT_ON = "software_support_on"
HARDWARE_SEND_ON_ONLY = "hardware_send_on_only"
HARDWARE_NIGHT_MODE = "hardware_night_mode"
HARDWARE_LED_OFF = "hardware_led_off"
RELAY_ON_SENSE_ON = "relay_on_sense_on"
MOMENTARY_MODE_ON = "momentary_on"
MOMENTARY_ON_OFF_TRIGGER = "momentary_on_off_trigger"
SENSE_SENDS_OFF = "sense_sends_off"
MOMENTARY_FOLLOW_SENSE = "momentary_follow_sense"
INSTEON_OFF = "insteon_off"
CHECKSUM_OFF = "checksum_off"
STANDARD_HOLDOFF = "standard_holdoff"
DUAL_LINE_ON = "dual_line_on"
LATCHING_ON = "latching_on"
THREE_WAY_ON = "three_way_on"
REVERSED_ON = "reversed_on"
FORWARD_ON = "forward_on"
MOMENTARY_LINE_ON = "momentary_line_on"
NOT_3_WAY = "not_3_way"
CRC_ERROR_COUNT = "crc_error_count"
SIGNAL_TO_NOISE_OF_LAST_FAILURE = "signal_to_noise_of_last_failure"
SIGNAL_TO_NOISE_FAILURE_COUNT = "signal_to_noise_failure_count"
DATABASE_DELTA = "database_delta"
CELSIUS = "celsius"
TIME_24_HOUR_FORMAT = "time_24_hour_format"
SOFTWARE_LOCK_ON = "SOFTWARE_LOCK_ON"

# Extended Properties
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

# Derived Properties
MOMENTARY_DELAY = "momentary_delay"
RADIO_BUTTON_GROUPS = "radio_button_groups"
RAMP_RATE_IN_SEC = "ramp_rate_in_seconds"
RELAY_MODE = "relay_mode"
TOGGLE_BUTTON = "toggle_button"


def calc_toggle_mode(toggle_value, toggle_on_value):
    """Calculate the toggle mode value."""
    if not toggle_value:
        return ToggleMode.TOGGLE
    if toggle_on_value:
        return ToggleMode.ON_ONLY
    return ToggleMode.OFF_ONLY


def get_usable_value(prop):
    """Return the current or new value of the property."""
    return prop.new_value if prop.is_dirty else prop.value
