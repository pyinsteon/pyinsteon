"""Operating flags list."""
from .device_flag import DeviceFlagBase

PROGRAM_LOCK_ON = 'program_lock_on'
LED_ON = 'led_on'
LED_OFF = 'led_off'
KEY_BEEP_ON = 'key_beep_on'
STAY_AWAKE_ON = 'stay_awake_on'
LISTEN_ONLY_ON = 'listen_only_on'
HEART_BEAT_ON = 'heart_beat_on'
HEART_BEAT_OFF = 'heart_beat_off'
ON_ONLY_ON = 'on_only_on'
GROUPED_ON = 'grouped_on'
RESUME_DIM_ON = 'resume_dim_on'
RF_DISABLE_ON = 'rf_disable_on'
POWERLINE_DISABLE_ON = 'powerline_disable_on'
TEND_ON = 'tend_on'
X10_OFF = 'x10_off'
CLEANUP_REPORT_ON = 'cleanup_report_on'
DETACH_LOAD_ON = 'detach_load_on'
SMART_HOPS_ON = 'smart_hops_on'
LED_BLINK_ON_ERROR_ON = 'blink_on_error_on'
LED_BLINK_ON_TX_ON = 'blink_on_tx_on'
REPEAT_OPEN_ON = 'repeat_open_on'
REPEAT_CLOSED_ON = 'repeat_closed_on'
LINK_TO_FF_GROUP = 'link_to_ff_group'
LOAD_SENSE_ON = 'load_sense_on'
LOAD_SENSE_2_ON = 'load_sense_2_on'

DUAL_LINE_ON = 'dual_line_on'
LATCHING_ON = 'latching_on'
THREE_WAY_ON = 'three_way_on'
REVERSED_ON = 'reversed_on'
MOMENTARY_LINE_ON = 'momentary_line_on'
NOT_3_WAY = 'not_3_way'

CRC_ERROR_COUNT = 'crc_error_count'
SIGNAL_TO_NOISE_OF_LAST_FAILURE = 'signal_to_noise_of_last_failure'
SIGNAL_TO_NOISE_FAILURE_COUNT = 'signal_to_noise_failure_count'
DATABASE_DELTA = 'database_delta'

class OperatingFlag(DeviceFlagBase):
    """Operating flag for a device."""
