"""Operating flags for all device types."""
import logging

_LOGGER = logging.getLogger(__name__)

PROGRAM_LOCK_ON = 'program_lock_on'
LED_ON = 'led_on'
KEY_BEEP_ON = 'key_beep_on'
STAY_AWAKE_ON = 'stay_awake_on'
LISTEN_ONLY_ON = 'listen_only'
HEART_BEAT_ON = 'heart_beat'
GROUPED_ON = 'grouped'
DATABASE_DELTA = 'database_delta'
RESUME_DIM_ON = 'resume_dim'
RF_DISABLE = 'rf_disable'
POWERLINE_DISABLE = 'powerline_disable'
CRC_ERROR_COUNT = 'crc_error_count'
TEND_ON = 'tend'
NO_X10 = 'no_x10'
CLEANUP_REPORT_ON = 'cleanup_report'
DETACH_LOAD_ON = 'detach_load'
SMART_HOPS_ON = 'smart_hops'
SIGNAL_TO_NOISE_OF_LAST_FAILURE = 'signal_to_noise_of_last_failure'
SIGNAL_TO_NOISE_FAILURE_COUNT = 'signal_to_noise_failure_count'
LED_BLINK_ON_ERROR = 'blink_on_error'
LED_BLINK_ON_TX = 'blink_on_tx'
REPEAT_OPEN_ON = 'repeat_open'
REPEAT_CLOSED_ON = 'repeat_closed'
LINK_TO_FF_GROUP = 'link_to_ff_group'
LED_OFF = 'led_off'
LOAD_SENSE_ON = 'load_sense_on'
LOAD_SENSE_2_ON = 'load_sense_2_on'
DUAL_LINE = 'dual_line'
MOMENTARY_LINE = 'momentary_line'
NOT_3_WAY = 'not_3_way'


class OperatingFlags():
    """Operating flags."""

    _flags = {}

    def __init__(self, name0='bit0', name1='bit1', name2='bit2', name3='bit3',
                 name4='bit4', name5='bit5', name6='bit6', name7='bit7'):
        self._flags = {}
        self._names = {}
        self._is_dirty = False
        names = [(name0, 0),
                 (name1, 1),
                 (name2, 2),
                 (name3, 3),
                 (name4, 4),
                 (name5, 5),
                 (name6, 6),
                 (name7, 7)]
        self._map_keys(names)

    def __setitem__(self, key, value):
        """Add an operating flag bit."""
        bit = self._get_bit_from_key(key)
        self._flags[bit] = bool(value)
        self._is_dirty = True

    def __getitem__(self, key):
        """Return the value of the operating flag."""
        bit = self._get_bit_from_key(key)
        return self._flags[bit]

    def __iter__(self):
        """Return the flag keys."""
        for bit in self._names:
            yield self._names[bit]

    def __bytes__(self):
        """Return the bytes value of the operating flags."""
        return bytes([int(self)])

    def __int__(self):
        """Return the integer value of the operating flags."""
        byte_value = 0x00
        for bit in range(0, 7):
            value = 1 if self._flags[bit] else 0
            if value:
                byte_value = byte_value | value << bit
            else:
                mask = 0xff - (value << bit)
                byte_value = byte_value & mask
        return byte_value

    def add_handler(self, handler):
        """Subscribe to a handler to set the value of the state."""
        handler.subscribe(self.set_value)

    #pylint: disable=unused-variable
    def set_value(self, flags):
        """Set the operating flags based on the device value.

        This method does not set the `is_dirty` flag.
        Only use this method when loading the flags from the device.
        """
        if isinstance(flags, (bytes, bytearray)):
            flags = int.from_bytes(flags, byteorder='big')
        for bit in range(0, 8):
            self._flags[bit] = bool(flags & 1 << bit)

    def _get_bit_from_key(self, key):
        """Return the bit number from the operating flag name."""
        if not isinstance(key, str) and not isinstance(key, int):
            raise KeyError
        if isinstance(key, str):
            for bit in self._names:
                if self._names[bit] == key:
                    return bit
        return key

    def _map_keys(self, names):
        for name, bit in names:
            self._flags[bit] = False
            self._names[bit] = name
