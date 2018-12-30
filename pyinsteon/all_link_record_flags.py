"""All-Link Record Flags."""

from binascii import hexlify
from .utils import bit_is_set, set_bit
from .constants import AllLinkMode


class AllLinkRecordFlags():
    """All-Link Record Flags."""

    def __init__(self, data: int):
        """Init the AllLinkRecordFlags class."""
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

    @property
    def is_in_use(self):
        """Return if record is in use."""
        return self._in_use

    @property
    def mode(self):
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

    @property
    def bytes(self):
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

    @property
    def hex(self):
        """Return the hex representation of the flags."""
        return hexlify(self.bytes).decode()