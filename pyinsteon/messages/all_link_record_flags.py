"""All-Link Record Flags."""

from binascii import hexlify
from ..utils import bit_is_set, set_bit, test_values_eq
from ..constants import AllLinkMode


def create(in_use: bool, mode: AllLinkMode, hwm: bool,
           bit5: bool = False, bit4: bool = False,
           bit3: bool = False, bit2: bool = False,
           bit0: bool = False):
    """Create an AllLinkRecordFlags entity."""
    flags = AllLinkRecordFlags(0x00)
    flags.is_bit_0_set = bit0
    flags.is_bit_2_set = bit2
    flags.is_bit_3_set = bit3
    flags.is_bit_4_set = bit4
    flags.is_bit_5_set = bit5
    flags.is_hwm = hwm
    flags.is_in_use = in_use
    flags.mode = mode
    return flags


def create_template(in_use: bool = None, mode: AllLinkMode = None,
                    hwm: bool = None, bit5: bool = None, bit4: bool = None,
                    bit3: bool = None, bit2: bool = None,
                    bit0: bool = None):
    """Create an AllLinkRecordFlags entity."""
    flags = AllLinkRecordFlags(0x00)
    flags.is_bit_0_set = bit0
    flags.is_bit_2_set = bit2
    flags.is_bit_3_set = bit3
    flags.is_bit_4_set = bit4
    flags.is_bit_5_set = bit5
    flags.is_hwm = hwm
    flags.is_in_use = in_use
    flags.mode = mode
    return flags


def _normalize(data):
    if isinstance(data, AllLinkRecordFlags):
        return bytes(data)
    return data


class AllLinkRecordFlags():
    """All-Link Record Flags."""

    def __init__(self, data: int):
        """Init the AllLinkRecordFlags class."""
        data = _normalize(data)
        if isinstance(data, bytes):
            data = int.from_bytes(data, byteorder="big")
        self._in_use = bit_is_set(data, 7)
        is_controller = bit_is_set(data, 6)
        self._mode = AllLinkMode(0)
        if is_controller:
            self._mode = AllLinkMode(1)
        self._bit5 = bit_is_set(data, 5)
        self._bit4 = bit_is_set(data, 4)
        self._bit3 = bit_is_set(data, 3)
        self._bit2 = bit_is_set(data, 2)
        self._hwm = not bit_is_set(data, 1)
        self._bit0 = bit_is_set(data, 0)

    def __bytes__(self):
        """Return the byte representation of the flags."""
        flags = 0x00
        flags = set_bit(flags, 7, self._in_use)
        flags = set_bit(flags, 6, bool(self._mode.value))
        flags = set_bit(flags, 5, self._bit5)
        flags = set_bit(flags, 4, self._bit4)
        flags = set_bit(flags, 3, self._bit3)
        flags = set_bit(flags, 2, self._bit2)
        flags = set_bit(flags, 1, not self._hwm)
        flags = set_bit(flags, 0, self._bit0)
        return bytes([flags])

    def __repr__(self):
        """Return the hex representation of the flags."""
        val = {'in use': 1 if self.is_in_use else 0,
               'mode': 1 if bool(self.mode.value) else 0,
               'bit5': 1 if self.is_bit_5_set else 0,
               'bit4': 1 if self.is_bit_4_set else 0,
               'bit3': 1 if self.is_bit_3_set else 0,
               'bit2': 1 if self.is_bit_2_set else 0,
               'hwm': 0 if self.is_hwm else 1,
               'bit0': 1 if self.is_bit_0_set else 0}
        return str(val)

    def __str__(self):
        """Return the hex representation of the flags."""
        return hexlify(bytes(self)).decode()

    def __eq__(self, other):
        """Check equality of this vs other."""
        if not isinstance(other, AllLinkRecordFlags):
            return False
        match = True
        match = match & test_values_eq(self.is_bit_0_set, other.is_bit_0_set)
        match = match & test_values_eq(self.is_bit_2_set, other.is_bit_2_set)
        match = match & test_values_eq(self.is_bit_3_set, other.is_bit_3_set)
        match = match & test_values_eq(self.is_bit_4_set, other.is_bit_4_set)
        match = match & test_values_eq(self.is_bit_5_set, other.is_bit_5_set)
        match = match & test_values_eq(self.is_in_use, other.is_in_use)
        match = match & test_values_eq(self.mode, other.mode)
        match = match & test_values_eq(self.is_hwm, other.is_hwm)
        return match

    @property
    def is_in_use(self):
        """Return if record is in use."""
        return self._in_use

    @is_in_use.setter
    def is_in_use(self, val: bool):
        """Set the record in use value."""
        if val is None:
            self._in_use = None
        else:
            self._in_use = bool(val)

    @property
    def mode(self):
        """Return if the record is a responder or controller."""
        return self._mode

    @mode.setter
    def mode(self, val: AllLinkMode):
        """Set the all link mode."""
        if val is None:
            self._mode = None
        elif isinstance(val, int):
            self._mode = AllLinkMode(val)
        elif isinstance(val, AllLinkMode):
            self._mode = val
        else:
            return TypeError("All link mode must be int, AllLinkMode or None")

    @property
    def is_hwm(self):
        """Return if the record is the high water mark."""
        return self._hwm

    @is_hwm.setter
    def is_hwm(self, val: bool):
        """Set the record High Water Mark value."""
        if val is None:
            self._hwm = None
        else:
            self._hwm = bool(val)

    @property
    def is_bit_5_set(self):
        """Return if bit 5 is set."""
        return self._bit5

    @is_bit_5_set.setter
    def is_bit_5_set(self, val: bool):
        """Set the record bit 5 value."""
        if val is None:
            self._bit5 = None
        else:
            self._bit5 = bool(val)

    @property
    def is_bit_4_set(self):
        """Return if bit 4 is set."""
        return self._bit4

    @is_bit_4_set.setter
    def is_bit_4_set(self, val: bool):
        """Set the record bit 4 value."""
        if val is None:
            self._bit4 = None
        else:
            self._bit4 = bool(val)

    @property
    def is_bit_3_set(self):
        """Return if bit 3 is set."""
        return self._bit3

    @is_bit_3_set.setter
    def is_bit_3_set(self, val: bool):
        """Set the record bit 3 value."""
        if val is None:
            self._bit3 = None
        else:
            self._bit3 = bool(val)

    @property
    def is_bit_2_set(self):
        """Return if bit 2 is set."""
        return self._bit2

    @is_bit_2_set.setter
    def is_bit_2_set(self, val: bool):
        """Set the record bit 2 value."""
        if val is None:
            self._bit2 = None
        else:
            self._bit2 = bool(val)

    @property
    def is_bit_0_set(self):
        """Return if bit 0 is set."""
        return self._bit0

    @is_bit_0_set.setter
    def is_bit_0_set(self, val: bool):
        """Set the record bit 0 value."""
        if val is None:
            self._bit0 = None
        else:
            self._bit0 = bool(val)
