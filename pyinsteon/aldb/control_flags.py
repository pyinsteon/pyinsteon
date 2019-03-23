"""ALDB Control Flags."""

def create_from_byte(control_flags):
    """Create a ControlFlags class from a control flags byte."""
    if isinstance(control_flags, bytes):
        control_flags = int.from_bytes(control_flags, 'big')
    in_use = bool(control_flags & 1 << 7)
    controller = bool(control_flags & 1 << 6)
    bit5 = bool(control_flags & 1 << 5)
    bit4 = bool(control_flags & 1 << 4)
    used_before = bool(control_flags & 1 << 1)
    flags = ControlFlags(in_use, controller, used_before, bit5=bit5, bit4=bit4)
    return flags


class ControlFlags():
    """Represents a ControlFlag byte of an ALDB record."""

    def __init__(self, in_use: bool, controller: bool, used_before: bool, bit5=0, bit4=0):
        """Init the ControlFlags Class."""
        self._in_use = bool(in_use)
        self._controller = bool(controller)
        self._used_before = bool(used_before)
        self._bit5 = bool(bit5)
        self._bit4 = bool(bit4)

    @property
    def is_in_use(self):
        """Return True if the record is in use."""
        return self._in_use

    @property
    def is_available(self):
        """Return True if the record is available for use."""
        return not self._in_use

    @property
    def is_controller(self):
        """Return True if the device is a controller."""
        return self._controller

    @property
    def is_responder(self):
        """Return True if the device is a responder."""
        return not self._controller

    @property
    def is_high_water_mark(self):
        """Return True if this is the last record."""
        return not self._used_before

    @property
    def is_used_before(self):
        """Return True if this is not the last record."""
        return self._used_before

    @property
    def byte(self):
        """Return a byte representation of ControlFlags."""
        flags = int(self._in_use) << 7 \
            | int(self._controller) << 6 \
            | int(self._bit5) << 5 \
            | int(self._bit4) << 4 \
            | int(self._used_before) << 1
        return flags
