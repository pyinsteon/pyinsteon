"""KeypadLink radio button property."""
from itertools import chain

from ..utils import bit_is_set
from . import OFF_MASK, ON_MASK, get_usable_value
from .derived_property import DerivedProperty


def sort_groups(groups):
    """Sort the radio button groups from smallest to largest."""
    for group in groups:
        group.sort()
    groups.sort()
    return groups


def on_mask_name(button):
    """Return the name of the on mask for a button."""
    button_str = "" if button == 1 else f"_{button}"
    return f"{ON_MASK}{button_str}"


def off_mask_name(button):
    """Return the name of the off mask for a button."""
    button_str = "" if button == 1 else f"_{button}"
    return f"{OFF_MASK}{button_str}"


def calc_radio_button_groups(device, device_view=True):
    """Calculate the radio button groups based on the on masks.

    Set `device_view` to `True` to see the actual device setting.
    """
    rb_groups = []
    for button in device.groups:
        if button not in list(chain.from_iterable(rb_groups)):
            if device_view:
                on_mask = device.properties[on_mask_name(button)].value
            else:
                on_mask = get_usable_value(device.properties[on_mask_name(button)])
            if on_mask != 0:
                rb_group = [button]
                for bit in list(range(0, button - 1)) + list(range(button, 8)):
                    if bit_is_set(on_mask, bit):
                        rb_group.append(bit + 1)
                if len(rb_group) > 1:
                    rb_groups.append(rb_group)
    rb_groups = sort_groups(rb_groups)
    return rb_groups


def set_radio_buttons(device, radio_button_groups):
    """Set the radio button groups in the on and off mask properties."""
    group_lists = []
    for group in radio_button_groups:
        group = list(group)
        if len(group) < 2:
            raise ValueError("Cannot have a radio button group with one button.")
        group = [int(button) for button in group]
        group.sort()
        group_lists.append(group)
    group_lists = sort_groups(group_lists)
    reset_radio_button_groups(device)
    for new_group in group_lists:
        for button in new_group:
            if button not in device.groups:
                raise ValueError(f"Invalid button value: {button}")
        group_dirty = True
        for group in calc_radio_button_groups(device):
            if group == new_group:
                group_dirty = False
        if group_dirty:
            device.set_radio_buttons(new_group)

    clear_buttons = []
    for button in device.groups:
        if button == 1:
            continue
        button_in_group = False
        for group in radio_button_groups:
            if button in group:
                button_in_group = True
        if not button_in_group:
            clear_buttons.append(button)
    if clear_buttons:
        device.clear_radio_buttons(clear_buttons)


def reset_radio_button_groups(device):
    """Clear any dirty on or off mask properties."""
    for button in device.groups:
        device.properties[on_mask_name(button)].new_value = None
        device.properties[off_mask_name(button)].new_value = None


class RadioButtonGroupsProperty(DerivedProperty):
    """KeypadLink radio button groups property."""

    def __init__(
        self,
        device,
        name,
    ):
        """Init the RadioButtonGroupProperty class."""
        super().__init__(device.address, name, list, False, False)
        self._device = device

    @property
    def value(self):
        """Return the value of the radio button groups from the underlying properties."""
        return calc_radio_button_groups(self._device, device_view=True)

    @property
    def new_value(self):
        """Return the modified value of the property."""
        new_value = calc_radio_button_groups(self._device, device_view=False)
        if new_value == self.value:
            return None
        return new_value

    @new_value.setter
    def new_value(self, value):
        """Modify the value of the property.

        Set value to a list of lists (i.e. [[2, 3], [4, 5]]).

        Set `new_value` to `None` to retain the current groups.

        Set `new_value` to an empty set (i.e. `[]`) to remove all groups.
        """

        if value is None:
            reset_radio_button_groups(self._device)
            return

        set_radio_buttons(self._device, value)

    @property
    def is_dirty(self):
        """Return if the underlying property values have changed."""
        on_mask_status = [
            self._device.properties[on_mask_name(group)].is_dirty
            for group in self._device.groups
            if group != 1
        ]
        off_mask_status = [
            self._device.properties[off_mask_name(group)].is_dirty
            for group in self._device.groups
            if group != 1
        ]
        return any(on_mask_status) or any(off_mask_status)

    @property
    def is_loaded(self):
        """Return if the underlying property values are loaded.."""
        on_mask_status = [
            self._device.properties[on_mask_name(group)].is_loaded
            for group in self._device.groups
            if group != 1
        ]
        off_mask_status = [
            self._device.properties[off_mask_name(group)].is_loaded
            for group in self._device.groups
            if group != 1
        ]
        return all(on_mask_status) and all(off_mask_status)
