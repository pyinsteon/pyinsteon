"""IOLink momentary delay property."""
from . import get_usable_value
from .derived_property import DerivedProperty


class MomentaryDelayProperty(DerivedProperty):
    """IOLink momentary delay property."""

    def __init__(
        self,
        address,
        name,
        delay_prop,
        prescaler_prop,
    ):
        """Init the OnOffDelayProperty class."""
        super().__init__(address, name, float, False, False)

        self._delay_prop = delay_prop
        self._prescaler_prop = prescaler_prop

    @property
    def value(self):
        """Return the momentary delay value of the underlying proprties."""
        prescaler = max(self._prescaler_prop.value, 1)
        return self._delay_prop.value * prescaler / 10

    @property
    def new_value(self):
        """Return the new_value property."""
        if not (self._prescaler_prop.is_dirty or self._delay_prop.is_dirty):
            return None
        prescaler = get_usable_value(self._prescaler_prop)
        delay = get_usable_value(self._delay_prop)
        prescaler = max(prescaler, 1)
        return delay * prescaler / 10

    @new_value.setter
    def new_value(self, value):
        """Set the new_value property."""
        seconds = self._value_type(value)

        if not 0 < seconds < 6502:  # 255^2 / 10  or about 1 hour 48 min
            raise ValueError

        if seconds == self.value:
            self._delay_prop.new_value = None
            self._prescaler_prop.new_value = None
            return

        delay = seconds * 10
        prescaler = 1
        if delay > 255:
            prescaler = int(round(delay / 255 + 0.5, 0))
            delay = int(round(delay / prescaler, 0))
        self._prescaler_prop.new_value = prescaler
        self._delay_prop.new_value = delay

    @property
    def is_dirty(self):
        """Return the change status of the underlying properties."""
        return self._delay_prop.is_dirty or self._prescaler_prop.is_dirty

    @property
    def is_loaded(self):
        """Return the load status of the underlying properties."""
        return self._delay_prop.is_loaded and self._prescaler_prop.is_loaded
