"""IOLink relay mode property."""
from ..constants import RelayMode
from . import RELAY_MODE, get_usable_value
from .derived_property import DerivedProperty


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


class RelayModeProperty(DerivedProperty):
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
        super().__init__(address, RELAY_MODE, RelayMode, False, False)

        self._momentary_mode_on_prop = momentary_mode_on_prop
        self._momentary_follow_sense_prop = momentary_follow_sense_prop
        self._momentary_on_off_trigger_prop = momentary_on_off_trigger_prop

    @property
    def value(self):
        """Return the relay mode based on the underlying properties."""
        on_prop = self._momentary_mode_on_prop
        f_prop = self._momentary_follow_sense_prop
        oo_prop = self._momentary_on_off_trigger_prop

        return _calc_relay_mode(on_prop.value, f_prop.value, oo_prop.value)

    @property
    def new_value(self):
        """Return the new_value property."""
        on_val = get_usable_value(self._momentary_mode_on_prop)
        follow_val = get_usable_value(self._momentary_follow_sense_prop)
        on_off_val = get_usable_value(self._momentary_on_off_trigger_prop)

        new_value = _calc_relay_mode(on_val, follow_val, on_off_val)
        if new_value == self.value:
            return None
        return new_value

    @new_value.setter
    def new_value(self, value):
        """Set the new_value property."""

        def set_relay_mode(momentary_mode_on, momentary_follow_sense, momentary_on_off):
            """Set the values of the underlying properties."""
            self._momentary_mode_on_prop.new_value = momentary_mode_on
            self._momentary_follow_sense_prop.new_value = momentary_follow_sense
            self._momentary_on_off_trigger_prop.new_value = momentary_on_off

        if value is None:
            set_relay_mode(None, None, None)
            return

        relay_mode = RelayMode(int(value))
        if relay_mode == self.value:
            set_relay_mode(None, None, None)
            return

        if relay_mode == RelayMode.LATCHING:
            set_relay_mode(False, False, False)
        elif relay_mode == RelayMode.MOMENTARY_A:
            set_relay_mode(True, False, False)
        elif relay_mode == RelayMode.MOMENTARY_B:
            set_relay_mode(True, False, True)
        elif relay_mode == RelayMode.MOMENTARY_C:
            set_relay_mode(True, True, False)

    @property
    def is_dirty(self):
        """Return the change status of the property."""
        return (
            self._momentary_follow_sense_prop.is_dirty
            or self._momentary_mode_on_prop.is_dirty
            or self._momentary_on_off_trigger_prop.is_dirty
        )

    @property
    def is_loaded(self):
        """Return the change status of the property."""
        return (
            self._momentary_follow_sense_prop.is_loaded
            and self._momentary_mode_on_prop.is_loaded
            and self._momentary_on_off_trigger_prop.is_loaded
        )
