"""All-Link Record Flags."""

from binascii import hexlify
from ..utils import bit_is_set, set_bit

def create(auto_link: bool, monitor_mode: bool, auto_led: bool,
           disable_deadman: bool):
    """Create an IM Configuration Flag entity."""
    flags = set_bit(0x00, 7, auto_link)
    flags = set_bit(flags, 6, monitor_mode)
    flags = set_bit(flags, 5, auto_led)
    flags = set_bit(flags, 4, disable_deadman)
    return IMConfigurationFlags(flags)

class IMConfigurationFlags():
    """IM Configuration Flags."""

    def __init__(self, data: int):
        """Init the IMConfigurationFlags class."""
        if isinstance(data, bytes):
            data = int.from_bytes(data, byteorder="big")
        self._auto_link = bit_is_set(data, 7)
        self._monitor_mode = bit_is_set(data, 6)
        self._auto_led = bit_is_set(data, 5)
        self._disable_deadman = bit_is_set(data, 4)

    def __bytes__(self):
        """Return the byte representation of the flags."""
        flags = set_bit(0x00, 7, self._auto_link)
        flags = set_bit(flags, 6, self._monitor_mode)
        flags = set_bit(flags, 5, self._auto_led)
        flags = set_bit(flags, 4, self._disable_deadman)
        return bytes([flags])

    def __repr__(self):
        """Return the hex representation of the flags."""
        val = {'auto link': 1 if self._auto_link else 0,
               'monitor mode': 1 if self._monitor_mode else 0,
               'auto led': 1 if self._auto_led else 0,
               'disable deadman': 1 if self._disable_deadman else 0}
        return str(val)

    def __str__(self):
        """Return the hex representation of the flags."""
        return hexlify(bytes(self)).decode()

    @property
    def is_auto_link(self):
        """Return if record is in use."""
        return self._auto_link

    @property
    def is_monitor_mode(self):
        """Return if the record is a responder or controller."""
        return self._monitor_mode

    @property
    def is_auto_led(self):
        """Return if the record is the high water mark."""
        return self._auto_led

    @property
    def is_disable_deadman(self):
        """Return if bit 5 is set."""
        return self._disable_deadman
