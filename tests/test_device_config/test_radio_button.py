"""Test the radio button groups property."""
from unittest import TestCase

from pyinsteon.config import RADIO_BUTTON_GROUPS
from pyinsteon.config.radio_button import off_mask_name, on_mask_name
from pyinsteon.device_types.dimmable_lighting_control import (
    DimmableLightingControl_KeypadLinc_8,
)

from ..utils import async_case, random_address

group1 = {2: 0x04, 3: 0x02}
group2 = {4: 0x10, 5: 0x08}
group3 = {6: 0xC0, 7: 0xA0, 8: 0x60}
group4 = {2: 0xA8, 4: 0xA2, 6: 0x8A, 8: 0x2A}


def reset_properties(device, value=0):
    """Reset the on / off mask values to 0."""
    for button in device.groups:
        on_mask_prop = device.properties[on_mask_name(button)]
        off_mask_prop = device.properties[off_mask_name(button)]
        on_mask_prop.load(value)
        off_mask_prop.load(value)


class TestRadioButtonGroupsProperty(TestCase):
    """Test the momentary delay flag."""

    @async_case
    async def test_new_value(self):
        """Test the momentary delay value."""
        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(address, 0x01, 0x02)
        test_prop = device.configuration[RADIO_BUTTON_GROUPS]

        # Test a single group
        for test_group in [group1, group2, group3, group4]:
            reset_properties(device)
            test_prop.new_value = [test_group.keys()]
            for k, v in test_group.items():
                assert device.properties[on_mask_name(k)].new_value == v
                assert device.properties[off_mask_name(k)].new_value == v
            clear_buttons = []
            for button in range(1, 9):
                if button not in test_group:
                    clear_buttons.append(button)
            for button in clear_buttons:
                assert device.properties[on_mask_name(button)].new_value is None
                assert device.properties[off_mask_name(button)].new_value is None

        # Test two groups
        reset_properties(device)
        test_prop.new_value = [group1.keys(), group3.keys()]
        for test_group in [group1, group3]:
            for k, v in test_group.items():
                assert device.properties[on_mask_name(k)].new_value == v
                assert device.properties[off_mask_name(k)].new_value == v
        clear_buttons = []
        for button in range(1, 9):
            if button not in group1 and button not in group3:
                clear_buttons.append(button)
        for button in clear_buttons:
            assert device.properties[on_mask_name(button)].new_value is None
            assert device.properties[off_mask_name(button)].new_value is None

        # Test new_value from underlying properties
        reset_properties(device)
        for k, v in group1.items():
            device.properties[on_mask_name(k)].new_value = v
            device.properties[off_mask_name(k)].new_value = v
            assert test_prop.new_value == [[2, 3]]

        # Test resetting properties:
        test_prop.new_value = None
        for k, v in group1.items():
            assert device.properties[on_mask_name(k)].new_value is None
            assert device.properties[off_mask_name(k)].new_value is None

        # Test clearing all properties
        reset_properties(device)
        for k, v in group1.items():
            device.properties[on_mask_name(k)].load(v)
            device.properties[off_mask_name(k)].load(v)
        assert test_prop.value == [[2, 3]]
        assert test_prop.new_value is None

        test_prop.new_value = []
        for k, v in group1.items():
            assert device.properties[on_mask_name(k)].new_value == 0
            assert device.properties[off_mask_name(k)].new_value == 0

        # Test bad button number
        try:
            test_prop.new_value = [[2, 9]]
            assert False
        except ValueError:
            assert True

        # Test changing one group leaving a second group alone
        reset_properties(device)
        for k, v in group1.items():
            device.properties[on_mask_name(k)].load(v)
            device.properties[off_mask_name(k)].load(v)
            assert test_prop.value == [[2, 3]]
        test_prop.new_value = [group1.keys(), group3.keys()]
        for k, v in group1.items():
            assert device.properties[on_mask_name(k)].new_value is None
            assert device.properties[off_mask_name(k)].new_value is None
            assert device.properties[on_mask_name(k)].value == v
            assert device.properties[off_mask_name(k)].value == v
        for k, v in group3.items():
            assert device.properties[on_mask_name(k)].new_value == v
            assert device.properties[off_mask_name(k)].new_value == v

        # Test a single button group
        reset_properties(device)
        try:
            test_prop.new_value = [[2]]
            assert False
        except ValueError:
            assert True

    @async_case
    async def test_is_dirty(self):
        """Test the is_dirty property."""
        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(address, 0x01, 0x02)
        test_prop = device.configuration[RADIO_BUTTON_GROUPS]

        reset_properties(device)
        assert not test_prop.is_dirty
        for k, v in group1.items():
            device.properties[on_mask_name(k)].load(v)
            device.properties[off_mask_name(k)].load(v)
        assert not test_prop.is_dirty

        # Set the underlying properties new_value
        device.properties[on_mask_name(2)].new_value = group1[2] + 1
        assert test_prop.is_dirty
        device.properties[on_mask_name(2)].new_value = None
        assert not test_prop.is_dirty
        device.properties[off_mask_name(2)].new_value = group1[2] + 1
        assert test_prop.is_dirty

        # Reset the underlying properties
        device.properties[on_mask_name(2)].new_value = None
        device.properties[off_mask_name(2)].new_value = None
        assert not test_prop.is_dirty

    @async_case
    async def test_is_loaded(self):
        """Test the is_dirty property."""
        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(address, 0x01, 0x02)
        test_prop = device.configuration[RADIO_BUTTON_GROUPS]

        for button in device.groups:
            if button == 1:
                continue
            assert not test_prop.is_loaded
            device.properties[on_mask_name(button)].load(0)
            assert not test_prop.is_loaded
            device.properties[off_mask_name(button)].load(0)
        assert test_prop.is_loaded
