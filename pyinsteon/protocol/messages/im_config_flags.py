"""All-Link Record Flags."""

from binascii import hexlify

from ...utils import bit_is_set, set_bit


def create(auto_link: bool, monitor_mode: bool, auto_led: bool, disable_deadman: bool):
    """Create an IM Configuration Flag entity."""
    flags = IMConfigurationFlags(0x00)
    flags.is_auto_link = auto_link
    flags.is_monitor_mode = monitor_mode
    flags.is_auto_led = auto_led
    flags.is_disable_deadman = disable_deadman
    return flags


def create_template(
    auto_link: bool = None,
    monitor_mode: bool = None,
    auto_led: bool = None,
    disable_deadman: bool = None,
):
    """Create an IM Configuration Flag entity."""
    flags = IMConfigurationFlags(0x00)
    flags.is_auto_link = auto_link
    flags.is_monitor_mode = monitor_mode
    flags.is_auto_led = auto_led
    flags.is_disable_deadman = disable_deadman
    return flags


def _normalize(data):
    if isinstance(data, IMConfigurationFlags):
        return bytes(data)
    return data


class IMConfigurationFlags:
    """IM Configuration Flags."""

    def __init__(self, data: int):
        """Init the IMConfigurationFlags class."""
        data = _normalize(data)
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
        val = {
            "auto link": 1 if self._auto_link else 0,
            "monitor mode": 1 if self._monitor_mode else 0,
            "auto led": 1 if self._auto_led else 0,
            "disable deadman": 1 if self._disable_deadman else 0,
        }
        return str(val)

    def __str__(self):
        """Return the hex representation of the flags."""
        return hexlify(bytes(self)).decode()

    def __eq__(self, other):
        """Check if this is equal to other."""
        if not isinstance(other, IMConfigurationFlags):
            return False
        return (
            self.is_auto_link == other.is_auto_link
            and self.is_monitor_mode == other.is_monitor_mode
            and self.is_auto_led == other.is_auto_led
            and self.is_disable_deadman == other.is_disable_deadman
        )

    def __hash__(self):
        """Represent the IMConfigurationFlags class as a hash."""
        return hash(bytes(self))

    @property
    def is_auto_link(self):
        """Return if record is in use."""
        return self._auto_link

    @is_auto_link.setter
    def is_auto_link(self, val: bool):
        """Set the auto link value."""
        if val is None:
            self._auto_link = None
        else:
            self._auto_link = bool(val)

    @property
    def is_monitor_mode(self):
        """Return if the record is a responder or controller."""
        return self._monitor_mode

    @is_monitor_mode.setter
    def is_monitor_mode(self, val: bool):
        """Set the monitoring mode value."""
        if val is None:
            self._monitor_mode = None
        else:
            self._monitor_mode = bool(val)

    @property
    def is_auto_led(self):
        """Return if the record is the high water mark."""
        return self._auto_led

    @is_auto_led.setter
    def is_auto_led(self, val: bool):
        """Set the auto LED value."""
        if val is None:
            self._auto_led = None
        else:
            self._auto_led = bool(val)

    @property
    def is_disable_deadman(self):
        """Return if disable deadman is set."""
        return self._disable_deadman

    @is_disable_deadman.setter
    def is_disable_deadman(self, val: bool):
        """Set the disable deadman value."""
        if val is None:
            self._disable_deadman = None
        else:
            self._disable_deadman = bool(val)
