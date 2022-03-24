"""Test the toggle button flag."""
from unittest import TestCase

from pyinsteon.config.extended_property import ExtendedProperty
from pyinsteon.config.toggle_button import ToggleButtonProperty
from pyinsteon.constants import PropertyType, ToggleMode
from pyinsteon.utils import set_bit

from ..utils import random_address

test_toggle_mode_to_prop = {
    ToggleMode.TOGGLE: [False, False],
    ToggleMode.ON_ONLY: [True, True],
    ToggleMode.OFF_ONLY: [True, False],
}


class TestToggleButtonProperty(TestCase):
    """Test the toggle button flag."""

    def test_value(self):
        """Test the toggle button value."""
        address = random_address()

        for button in range(2, 8):
            non_toggle_prop = ExtendedProperty(
                address, "non_toggle", int, False, False, PropertyType.ADVANCED
            )
            on_only_prop = ExtendedProperty(
                address, "on_only", int, False, False, PropertyType.ADVANCED
            )
            test_prop = ToggleButtonProperty(
                address,
                "test_prop",
                button,
                non_toggle_prop,
                on_only_prop,
            )
            assert test_prop.value is None

            for toggle_mode, test_values in test_toggle_mode_to_prop.items():
                non_toggle_prop.load(set_bit(0, button - 1, test_values[0]))
                on_only_prop.load(set_bit(0, button - 1, test_values[1]))
                assert test_prop.value == toggle_mode

    def test_new_value(self):
        """Test the new_value property."""
        address = random_address()
        non_toggle_prop = ExtendedProperty(
            address, "non_toggle", int, False, False, PropertyType.ADVANCED
        )
        on_only_prop = ExtendedProperty(
            address, "on_only", int, False, False, PropertyType.ADVANCED
        )

        for button in range(2, 8):
            test_prop = ToggleButtonProperty(
                address,
                "test_prop",
                button,
                non_toggle_prop,
                on_only_prop,
            )

            # Test the new_value is calculated correctly from the underlying properties
            for toggle_mode, test_values in test_toggle_mode_to_prop.items():
                non_toggle_prop.load(set_bit(0, button - 1, not test_values[0]))
                on_only_prop.load(set_bit(0, button - 1, not test_values[1]))
                assert test_prop.new_value is None
                non_toggle_prop.new_value = set_bit(0, button - 1, test_values[0])
                on_only_prop.new_value = set_bit(0, button - 1, test_values[1])
                assert test_prop.new_value == toggle_mode

            # Test the underlying properties are set correctly
            for toggle_mode, test_values in test_toggle_mode_to_prop.items():
                non_toggle_prop.load(set_bit(0, button - 1, not test_values[0]))
                on_only_prop.load(set_bit(0, button - 1, not test_values[1]))
                assert test_prop.new_value is None
                test_prop.new_value = toggle_mode
                assert non_toggle_prop.new_value == set_bit(
                    0, button - 1, test_values[0]
                )
                assert on_only_prop.new_value == set_bit(0, button - 1, test_values[1])
                test_prop.new_value = None
                assert non_toggle_prop.new_value is None
                assert on_only_prop.new_value is None

                test_prop.new_value = toggle_mode
                assert non_toggle_prop.new_value == set_bit(
                    0, button - 1, test_values[0]
                )
                assert on_only_prop.new_value == set_bit(0, button - 1, test_values[1])
                test_prop.new_value = test_prop.value
                assert non_toggle_prop.new_value is None
                assert on_only_prop.new_value is None
