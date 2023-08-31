"""Operating flag byte for a property read/write process.

For use with `ExtendedPropertyReadManager` and `ExtendedPropertyWriteManager`.

- Receives a list of operating flags and the associated bit.
- Stores the value of a property byte just like any other property.
- Updates the associated operating flags with the correct value based on the bit mapping.
- For bits that do not have an operating flag, the underlying `_value` property will determine the bit value.

"""
from typing import Dict

from ..constants import PropertyType
from ..utils import bit_is_set, set_bit
from .device_flag import DeviceFlagBase
from .operating_flag import OperatingFlag


def _value(prop: OperatingFlag):
    return prop.new_value if prop.is_dirty else prop.value


class OpFlagPropertyByte(DeviceFlagBase):
    """Operating flag byte for a property read/write process.

    For use with `ExtendedPropertyReadManager` and `ExtendedPropertyWriteManager`.
    """

    def __init__(
        self, address, name, flags: Dict[int, OperatingFlag], is_read_only=False
    ):
        """Init the DerivedProperty class."""
        super().__init__(
            address,
            "derived_property",
            name,
            int,
            is_reversed=False,
            is_read_only=is_read_only,
        )
        self._flags: Dict[int, OperatingFlag] = flags
        self._prop_type = PropertyType.HIDDEN

    @property
    def is_dirty(self):
        """Return if any of the operating flags are dirty."""
        for _, prop in self._flags.items():
            if prop.is_dirty:
                return True
        return False

    @property
    def is_loaded(self):
        """Return if the Operating flag has been loaded."""
        for _, prop in self._flags.items():
            if not prop.is_loaded:
                return False
        return True

    @property
    def value(self):
        """Return the value of the flag."""
        byte_value = self._value if self._value is not None else 0x00
        for bit, prop in self._flags.items():
            if prop.value is None:
                return None
            byte_value = set_bit(byte_value, bit, prop.value)
        return byte_value

    @property
    def new_value(self):
        """Return the new value of the flag."""
        byte_value = self.value
        for bit, prop in self._flags.items():
            if prop.value is None:
                return None
            value = _value(prop)
            byte_value = set_bit(byte_value, bit, value)
        return byte_value

    @new_value.setter
    def new_value(self, value):
        """Set the new value of the flag.

        This is the primary method to set the value of the flag.
        It sets the `new_value` property and the `is_dirty` property.
        """
        for bit, prop in self._flags.items():
            new_val = bit_is_set(value, bit) if value is not None else None
            prop.new_value = new_val

    def set_value(self, value):
        """Load the flag from the device value.

        Only use this method to update the value of the flag from the value
        of the device.

        This method updates the `is_loaded` property and clears the `new value` and
        `is_dirty` properties.
        """
        super().set_value(value=value)
        for bit, prop in self._flags.items():
            if value is None:
                new_val = None
            else:
                new_val = bit_is_set(value, bit)
            prop.set_value(new_val)
