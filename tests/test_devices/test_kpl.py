"""Test features specific to the KeyPadLinc."""


import unittest

from pyinsteon.device_types.dimmable_lighting_control import (
    DimmableLightingControl_KeypadLinc_8,
)
from pyinsteon.extended_property import (
    NON_TOGGLE_MASK,
    NON_TOGGLE_ON_OFF_MASK,
    OFF_MASK,
    ON_MASK,
)
from pyinsteon.utils import bit_is_set
from tests import set_log_levels
from tests.utils import random_address


class TestKeyPadLinkFeatures(unittest.TestCase):
    """Test setting the KeyPadLink features."""

    def setUp(self):
        """Set up the test."""
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_set_radio_buttons(self):
        """Test the `set_radio_buttons` feature."""

        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )
        device.set_radio_buttons([3, 4, 5, 6])

        masks = {
            1: None,
            2: None,
            3: int("00111000", 2),
            4: int("00110100", 2),
            5: int("00101100", 2),
            6: int("00011100", 2),
            7: None,
            8: None,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            assert on_mask.new_value == masks[button]
            assert off_mask.new_value == masks[button]

    def test_clear_radio_buttons(self):
        """Test the `set_radio_buttons` feature."""

        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            on_mask.load(0)
            off_mask.load(0)

        device.set_radio_buttons([3, 4, 5, 6])
        device.clear_radio_buttons([4, 5])

        masks = {
            1: None,
            2: None,
            3: int("00100000", 2),
            4: None,
            5: None,
            6: int("00000100", 2),
            7: None,
            8: None,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            assert on_mask.new_value == masks[button]
            assert off_mask.new_value == masks[button]

    def test_clear_radio_buttons_when_preset(self):
        """Test clearing an existing radio button group."""
        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )

        preset_masks = {
            1: 0,
            2: 0,
            3: int("00111000", 2),
            4: int("00110100", 2),
            5: int("00101100", 2),
            6: int("00011100", 2),
            7: 0,
            8: 0,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            on_mask.load(preset_masks[button])
            off_mask.load(preset_masks[button])

        device.clear_radio_buttons([4, 5])

        masks = {
            1: None,
            2: None,
            3: int("00100000", 2),
            4: 0,
            5: 0,
            6: int("00000100", 2),
            7: None,
            8: None,
        }

        for button in range(1, 9):
            button_str = f"_{button}" if button != 1 else ""
            on_mask = device.properties[f"{ON_MASK}{button_str}"]
            off_mask = device.properties[f"{OFF_MASK}{button_str}"]
            assert on_mask.new_value == masks[button]
            assert off_mask.new_value == masks[button]

    def test_set_toggle_mode(self):
        """Test setting toggle modes."""
        address = random_address()
        device = DimmableLightingControl_KeypadLinc_8(
            address, 0x01, 0x02, 0x03, "Test", "KPL"
        )

        device.properties[NON_TOGGLE_MASK].load(0)
        device.properties[NON_TOGGLE_ON_OFF_MASK].load(0)

        masks = {
            1: [0, 0],
            2: [0, 0],
            3: [1, 1],
            4: [1, 0],
            5: [0, 0],
            6: [0, 0],
            7: [0, 0],
            8: [0, 0],
        }

        device.set_toggle_mode(3, 1)
        device.set_toggle_mode(4, 2)

        for button in range(1, 9):
            non_toggle_mask = device.properties[NON_TOGGLE_MASK]
            non_toggle_on_off_mask = device.properties[NON_TOGGLE_ON_OFF_MASK]

            assert bit_is_set(non_toggle_mask.new_value, button - 1) == bool(
                masks[button][0]
            )
            assert bit_is_set(non_toggle_on_off_mask.new_value, button - 1) == bool(
                masks[button][1]
            )
