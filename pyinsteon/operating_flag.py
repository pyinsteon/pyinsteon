"""Operating flags list."""
from .address import Address
from .device_flag import DeviceFlagBase

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


class OperatingFlag(DeviceFlagBase):
    """Operating flag for a device."""

    def __init__(
        self, address, name, flag_type: type, is_reversed=False, is_read_only=False
    ):
        """Init the OperatingFlag class."""
        self._address = Address(address)
        topic = "{}.operating_flag.{}".format(self._address.id, name)
        super().__init__(topic, name, flag_type, is_reversed, is_read_only)
