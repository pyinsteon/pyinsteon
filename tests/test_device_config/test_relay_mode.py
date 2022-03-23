"""Test the momentary delay flag."""
from unittest import TestCase

from pyinsteon.config.extended_property import ExtendedProperty
from pyinsteon.config.relay_mode import RelayModeProperty
from pyinsteon.constants import PropertyType, RelayMode

from ..utils import random_address

test_prop_to_relay_mode = [
    [False, False, False, RelayMode.LATCHING],
    [False, True, False, RelayMode.LATCHING],
    [False, False, True, RelayMode.LATCHING],
    [False, True, True, RelayMode.LATCHING],
    [True, False, False, RelayMode.MOMENTARY_A],
    [True, False, True, RelayMode.MOMENTARY_B],
    [True, True, True, RelayMode.MOMENTARY_C],
    [True, True, False, RelayMode.MOMENTARY_C],
]
test_relay_mode_to_prop = {
    RelayMode.LATCHING: [False, False, False],
    RelayMode.MOMENTARY_A: [True, False, False],
    RelayMode.MOMENTARY_B: [True, False, True],
    RelayMode.MOMENTARY_C: [True, True, False],
}


class TestMomentaryDelayProperty(TestCase):
    """Test the momentary delay flag."""

    def test_value(self):
        """Test the momentary delay value."""
        address = random_address()

        momentary_mode_on_prop = ExtendedProperty(
            address, "mm_on", bool, False, False, PropertyType.ADVANCED
        )
        momentary_follow_sense_prop = ExtendedProperty(
            address, "m_follow", bool, False, False, PropertyType.ADVANCED
        )
        momentary_on_off_trigger_prop = ExtendedProperty(
            address, "m_on_off", bool, False, False, PropertyType.ADVANCED
        )

        test_prop = RelayModeProperty(
            address,
            "test_prop",
            momentary_mode_on_prop,
            momentary_follow_sense_prop,
            momentary_on_off_trigger_prop,
        )

        for test_value in test_prop_to_relay_mode:
            momentary_mode_on_prop.load(test_value[0])
            momentary_follow_sense_prop.load(test_value[1])
            momentary_on_off_trigger_prop.load(test_value[2])
            assert test_prop.value == test_value[3]

    def test_new_value(self):
        """Test the new_value property."""
        address = random_address()

        momentary_mode_on_prop = ExtendedProperty(
            address, "mm_on", bool, False, False, PropertyType.ADVANCED
        )
        momentary_follow_sense_prop = ExtendedProperty(
            address, "m_follow", bool, False, False, PropertyType.ADVANCED
        )
        momentary_on_off_trigger_prop = ExtendedProperty(
            address, "m_on_off", bool, False, False, PropertyType.ADVANCED
        )

        test_prop = RelayModeProperty(
            address,
            "test_prop",
            momentary_mode_on_prop,
            momentary_follow_sense_prop,
            momentary_on_off_trigger_prop,
        )

        for relay_mode, test_value in test_relay_mode_to_prop.items():
            # Make sure the new_value does not eq value otherwise no change is triggered
            momentary_mode_on_prop.load(not test_value[0])
            momentary_follow_sense_prop.load(not test_value[1])
            momentary_on_off_trigger_prop.load(not test_value[2])
            test_prop.new_value = relay_mode
            assert momentary_mode_on_prop.new_value == test_value[0]
            assert momentary_follow_sense_prop.new_value == test_value[1]
            assert momentary_on_off_trigger_prop.new_value == test_value[2]

        # Test resetting relay mode
        momentary_mode_on_prop.load(False)
        momentary_follow_sense_prop.load(False)
        momentary_on_off_trigger_prop.load(False)
        assert test_prop.value == RelayMode.LATCHING
        test_prop.new_value = RelayMode.MOMENTARY_A
        assert test_prop.new_value == RelayMode.MOMENTARY_A
        test_prop.new_value = RelayMode.LATCHING
        assert test_prop.new_value is None
        assert test_prop.value == RelayMode.LATCHING

        test_prop.new_value = RelayMode.MOMENTARY_A
        assert test_prop.new_value == RelayMode.MOMENTARY_A
        test_prop.new_value = None
        assert test_prop.new_value is None
        assert momentary_mode_on_prop.new_value is None
        assert momentary_follow_sense_prop.new_value is None
        assert momentary_on_off_trigger_prop.new_value is None

    def test_is_loaded(self):
        """Test the is_loaded property."""

        address = random_address()

        momentary_mode_on_prop = ExtendedProperty(
            address, "mm_on", bool, False, False, PropertyType.ADVANCED
        )
        momentary_follow_sense_prop = ExtendedProperty(
            address, "m_follow", bool, False, False, PropertyType.ADVANCED
        )
        momentary_on_off_trigger_prop = ExtendedProperty(
            address, "m_on_off", bool, False, False, PropertyType.ADVANCED
        )

        test_prop = RelayModeProperty(
            address,
            "test_prop",
            momentary_mode_on_prop,
            momentary_follow_sense_prop,
            momentary_on_off_trigger_prop,
        )
        assert not test_prop.is_loaded
        momentary_mode_on_prop.load(False)
        assert not test_prop.is_loaded
        momentary_follow_sense_prop.load(False)
        assert not test_prop.is_loaded
        momentary_on_off_trigger_prop.load(False)
        assert test_prop.is_loaded

    def test_is_dirty(self):
        """Test the id_dirty property."""

        address = random_address()

        momentary_mode_on_prop = ExtendedProperty(
            address, "mm_on", bool, False, False, PropertyType.ADVANCED
        )
        momentary_follow_sense_prop = ExtendedProperty(
            address, "m_follow", bool, False, False, PropertyType.ADVANCED
        )
        momentary_on_off_trigger_prop = ExtendedProperty(
            address, "m_on_off", bool, False, False, PropertyType.ADVANCED
        )

        test_prop = RelayModeProperty(
            address,
            "test_prop",
            momentary_mode_on_prop,
            momentary_follow_sense_prop,
            momentary_on_off_trigger_prop,
        )
        assert not test_prop.is_dirty
        momentary_mode_on_prop.load(False)
        assert not test_prop.is_dirty
        momentary_follow_sense_prop.load(False)
        assert not test_prop.is_dirty
        momentary_on_off_trigger_prop.load(False)
        assert not test_prop.is_dirty

        momentary_mode_on_prop.new_value = True
        assert test_prop.is_dirty
        momentary_mode_on_prop.new_value = None
        assert not test_prop.is_dirty

        momentary_follow_sense_prop.new_value = True
        assert test_prop.is_dirty
        momentary_follow_sense_prop.new_value = None
        assert not test_prop.is_dirty

        momentary_on_off_trigger_prop.new_value = True
        assert test_prop.is_dirty
        momentary_on_off_trigger_prop.new_value = None
        assert not test_prop.is_dirty
