"""KeypadLink toggle button property."""
from ..constants import ToggleMode
from ..utils import bit_is_set, set_bit
from . import calc_toggle_mode, get_usable_value
from .derived_property import DerivedProperty


class ToggleButtonProperty(DerivedProperty):
    """KeypadLink toggle button property."""

    def __init__(
        self, address, name, button, non_toggle_mask_prop, non_toggle_on_off_mask_prop
    ):
        """Init the ToggleButtonProperty class."""
        super().__init__(address, name, ToggleMode, False, False)
        self._button_bit = button - 1
        self._non_toggle_mask_prop = non_toggle_mask_prop
        self._non_toggle_on_off_mask_prop = non_toggle_on_off_mask_prop

    @property
    def value(self):
        """Return the toggle mode of the undlying properties."""
        if self.is_loaded:
            return None
        toggle_value = bit_is_set(self._non_toggle_mask_prop.value, self._button_bit)
        toggle_on_value = bit_is_set(
            self._non_toggle_on_off_mask_prop.value, self._button_bit
        )
        return calc_toggle_mode(toggle_value, toggle_on_value)

    @property
    def new_value(self):
        """Return the modified toggle mode of the button."""
        if not self.is_dirty:
            return None

        toggle_prop_value = get_usable_value(self._non_toggle_mask_prop)
        toggle_on_off_value = get_usable_value(self._non_toggle_on_off_mask_prop)
        toggle = bit_is_set(toggle_prop_value, self._button_bit)
        toggle_on = bit_is_set(toggle_on_off_value, self._button_bit)
        return calc_toggle_mode(toggle, toggle_on)

    @new_value.setter
    def new_value(self, value):
        """Set the new toggle mode value of the button."""
        if value is None:
            self._non_toggle_mask_prop.new_value = None
            self._non_toggle_on_off_mask_prop.new_value = None
            return

        toggle_mode = ToggleMode(value)
        if toggle_mode == self.value:
            self._non_toggle_mask_prop.new_value = None
            self._non_toggle_on_off_mask_prop.new_value = None
            return

        non_toggle_mask = self._non_toggle_mask_prop
        on_only_mask = self._non_toggle_on_off_mask_prop
        non_toggle_val = get_usable_value(non_toggle_mask)
        on_only_val = get_usable_value(on_only_mask)
        if toggle_mode == ToggleMode.TOGGLE:
            non_toggle_mask.new_value = set_bit(non_toggle_val, self._button_bit, False)
            on_only_mask.new_value = set_bit(on_only_val, self._button_bit, False)
        elif toggle_mode == ToggleMode.ON_ONLY:
            non_toggle_mask.new_value = set_bit(non_toggle_val, self._button_bit, True)
            on_only_mask.new_value = set_bit(on_only_val, self._button_bit, True)
        else:
            non_toggle_mask.new_value = set_bit(non_toggle_val, self._button_bit, True)
            on_only_mask.new_value = set_bit(on_only_val, self._button_bit, False)

    @property
    def is_dirty(self):
        """Return the change state of the underlying properties."""
        return (
            self._non_toggle_mask_prop.is_dirty
            or self._non_toggle_on_off_mask_prop.is_dirty
        )

    @property
    def is_loaded(self):
        """Return the load status of the underlying properties."""
        return (
            not self._non_toggle_mask_prop.is_loaded
            or not self._non_toggle_on_off_mask_prop.is_loaded
        )
