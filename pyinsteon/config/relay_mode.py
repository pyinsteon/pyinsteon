"""IOLink relay mode property."""
from ..address import Address
from ..constants import PropertyType, RelayMode
from .device_flag import DeviceFlagBase


def _calc_relay_mode(
    momentary_mode_on_value,
    momentary_follow_sense_value,
    momentary_on_off_trigger_value,
):
    """Calculate the relay mode."""
    if not momentary_mode_on_value:
        return RelayMode.LATCHING
    if momentary_follow_sense_value:
        return RelayMode.MOMENTARY_C
    if momentary_on_off_trigger_value:
        return RelayMode.MOMENTARY_B
    return RelayMode.MOMENTARY_A


class RelayModeProperty(DeviceFlagBase):
    """IOLink relay mode property."""

    def __init__(
        self,
        address,
        name,
        momentary_mode_on_prop,
        momentary_follow_sense_prop,
        momentary_on_off_trigger_prop,
    ):
        """Init the ExtendedProperty class."""
        self._address = Address(address)
        topic = f"{self._address.id}.property.{name}"
        super().__init__(topic, name, RelayMode, False, False, PropertyType.DERIVED)

        self._momentary_mode_on_prop = momentary_mode_on_prop
        self._momentary_follow_sense_prop = momentary_follow_sense_prop
        self._momentary_on_off_trigger_prop = momentary_on_off_trigger_prop

        self._momentary_mode_on_prop.subscribe(self._check_property_changes)
        self._momentary_follow_sense_prop.subscribe(self._check_property_changes)
        self._momentary_on_off_trigger_prop.subscribe(self._check_property_changes)

    @property
    def new_value(self):
        """Return the new_value property."""
        return super().new_value

    @new_value.setter
    def new_value(self, value):
        """Set the new_value property."""
        relay_mode = RelayMode(int(value))
        if relay_mode == self._value:
            self._new_value = None
            self._is_dirty = False
            return

        self._new_value = relay_mode
        self._is_dirty = True
        self._momentary_mode_on_prop.new_value = not (relay_mode == RelayMode.LATCHING)
        if relay_mode == RelayMode.MOMENTARY_A:
            self._momentary_follow_sense_prop.new_value = False
            self._momentary_on_off_trigger_prop.new_value = False
        if relay_mode == RelayMode.MOMENTARY_B:
            self._momentary_follow_sense_prop.new_value = False
            self._momentary_on_off_trigger_prop.new_value = True
        if relay_mode == RelayMode.MOMENTARY_C:
            self._momentary_follow_sense_prop.new_value = True
            self._momentary_on_off_trigger_prop.new_value = False

    def _check_property_changes(self, name, value):
        """Check for value change on property change."""
        on_prop = self._momentary_mode_on_prop
        f_prop = self._momentary_follow_sense_prop
        oo_prop = self._momentary_on_off_trigger_prop

        self._value = _calc_relay_mode(on_prop.value, f_prop.value, oo_prop.value)
        self._new_value = None
        self._is_dirty = False
        self._call_subscribers(name=self._name, value=self._value)

        if on_prop.is_dirty or f_prop.is_dirty or oo_prop.is_dirty:
            self._is_dirty = True
            on_val = on_prop.new_value if on_prop.is_dirty else on_prop.value
            follow_val = f_prop.new_value if f_prop.is_dirty else f_prop.value
            on_off_val = oo_prop.new_value if oo_prop.is_dirty else oo_prop.value
            self._new_value = _calc_relay_mode(on_val, follow_val, on_off_val)
