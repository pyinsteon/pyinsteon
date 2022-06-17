"""Derived property to hold an operating flag in an device property."""
from ..utils import bit_is_set, set_bit
from . import get_usable_value
from .derived_property import DerivedProperty


class OpFlagProperty(DerivedProperty):
    """Derived property to hold an operating flag in an device property."""

    def __init__(self, address, name, property, prop_bit):
        """Init the RampRateProperty class."""
        super().__init__(address, name, float, False, False)

        self._prop = property
        self._prop_bit = prop_bit

    @property
    def value(self):
        """Return the ramp rate property value in seconds."""
        return bit_is_set(self._prop.value, self._prop_bit)

    @property
    def new_value(self):
        """Return the ramp rate property in seconds."""
        if self._prop.new_value is None:
            return None
        curr_val = self.value
        new_val = bit_is_set(self._prop.new_value, self._prop_bit)
        if new_val == curr_val:
            return None
        return new_val

    @new_value.setter
    def new_value(self, value):
        """Set the ramp rate property in seconds."""
        if self._prop.value is None:
            new_value = 0
        else:
            new_value = get_usable_value(self._prop)

        if value is None:
            new_value = set_bit(new_value, self._prop_bit, self.value)
        else:
            new_value = set_bit(new_value, self._prop_bit, value)

        self._prop.new_value = new_value

    @property
    def is_loaded(self):
        """Return if the Operating flag has been loaded."""
        return self._prop.is_loaded

    @property
    def is_dirty(self):
        """Return if the Operating flag has been changed."""
        return self.new_value is None
