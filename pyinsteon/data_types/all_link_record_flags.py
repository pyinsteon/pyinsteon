"""All-Link Record Flags."""

from binascii import hexlify

from ..constants import AllLinkMode
from ..utils import bit_is_set, set_bit, test_values_eq


def _normalize(data):
    if isinstance(data, AllLinkRecordFlags):
        return bytes(data)
    return data


class AllLinkRecordFlags:
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

    def __int__(self):
        """Return the integer representation of the flags."""
        return int.from_bytes(bytes(self), byteorder="big")

    def __repr__(self):
        """Return the hex representation of the flags."""
        val = {
            "in use": 1 if self.is_in_use else 0,
            "link_mode": 1 if bool(self.link_mode.value) else 0,
            "bit5": 1 if self.is_bit_5_set else 0,
            "bit4": 1 if self.is_bit_4_set else 0,
            "bit3": 1 if self.is_bit_3_set else 0,
            "bit2": 1 if self.is_bit_2_set else 0,
            "hwm": 0 if self.is_hwm else 1,
            "bit0": 1 if self.is_bit_0_set else 0,
        }
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
        match = match & test_values_eq(self.link_mode, other.link_mode)
        match = match & test_values_eq(self.is_hwm, other.is_hwm)
        return match

    def __hash__(self):
        """Represent the AllLinkrecordFlags object as a hash."""
        return hash(bytes(self))

    @property
    def is_in_use(self):
        """Set the record in use value."""
        return self._in_use

    @property
    def link_mode(self):
        """Return if the record is a responder or controller."""
        return self._mode

    @property
    def is_hwm(self):
        """Return if the record is the high water mark."""
        return self._hwm

    @property
    def is_bit_5_set(self):
        """Return if bit 5 is set."""
        return self._bit5

    @property
    def is_bit_4_set(self):
        """Return if bit 4 is set."""
        return self._bit4

    @property
    def is_bit_3_set(self):
        """Return if bit 3 is set."""
        return self._bit3

    @property
    def is_bit_2_set(self):
        """Return if bit 2 is set."""
        return self._bit2

    @property
    def is_bit_0_set(self):
        """Return if bit 0 is set."""
        return self._bit0

    @classmethod
    def create(
        cls,
        in_use: bool,
        controller: bool,
        hwm: bool,
        bit5: bool = False,
        bit4: bool = False,
        bit3: bool = False,
        bit2: bool = False,
        bit0: bool = False,
    ):
        """Create an AllLinkRecordFlags entity."""
        flags = 0x00
        flags = set_bit(flags, 7, in_use)
        flags = set_bit(flags, 6, controller)
        flags = set_bit(flags, 5, bit5)
        flags = set_bit(flags, 4, bit4)
        flags = set_bit(flags, 3, bit3)
        flags = set_bit(flags, 2, bit2)
        flags = set_bit(flags, 1, not hwm)
        flags = set_bit(flags, 0, bit0)
        return cls(flags)
