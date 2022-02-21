"""IOLink momentary delay property."""
from ..address import Address
from ..constants import PropertyType
from .device_flag import DeviceFlagBase


class MomentaryDelayProperty(DeviceFlagBase):
    """IOLink momentary delay property."""

    def __init__(
        self,
        address,
        name,
        delay_prop,
        prescaler_prop,
    ):
        """Init the OnOffDelayProperty class."""
        self._address = Address(address)
        topic = f"{self._address.id}.property.{name}"
        super().__init__(topic, name, float, False, False, PropertyType.DERIVED)

        self._delay_prop = delay_prop
        self._prescaler_prop = prescaler_prop

        self._delay_prop.subscribe(self._check_property_changes)
        self._prescaler_prop.subscribe(self._check_property_changes)

    @property
    def new_value(self):
        """Return the new_value property."""
        return super().new_value

    @new_value.setter
    def new_value(self, value):
        """Set the new_value property."""
        seconds = self._value_type(value)
        if seconds == self._value:
            self._new_value = None
            self._is_dirty = False
            return

        if seconds > 6502:  # 255^2 / 10  or about 1 hour 48 min
            raise ValueError("Delay too large")

        self._new_value = seconds
        self._is_dirty = True
        delay = seconds * 10
        prescaler = 1
        if delay > 255:
            prescaler = int(round(delay / 255 + 0.5, 0))
            delay = int(round(delay / prescaler, 0))
        self._prescaler_prop.new_value = prescaler
        self._delay_prop.new_value = delay

    def _check_property_changes(self, name, value):
        """Check for changes to underlying properties."""
        prescaler = max(self._prescaler_prop.value, 1)
        self._value = self._delay_prop.value * prescaler / 10
        self._new_value = None
        self._is_dirty = None
        self._call_subscribers(name=self._name, value=self._value)

        if self._delay_prop.is_dirty or self._prescaler_prop.is_dirty:
            self._is_dirty = True
            ps_prop = self._prescaler_prop
            d_prop = self._delay_prop
            prescaler = ps_prop.new_value if ps_prop.is_dirty else ps_prop.value
            prescaler = max(prescaler, 1)
            delay = d_prop.new_value if d_prop.is_dirty else d_prop.value
            self._new_value = delay * prescaler / 10
