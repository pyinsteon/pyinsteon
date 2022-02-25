"""Test the momentary delay flag."""
from random import randint
from unittest import TestCase

from pyinsteon.config.extended_property import ExtendedProperty
from pyinsteon.config.momentary_delay import MomentaryDelayProperty
from pyinsteon.constants import PropertyType

from ..utils import random_address


class TestMomentaryDelayProperty(TestCase):
    """Test the momentary delay flag."""

    def test_value(self):
        """Test the momentary delay value."""
        address = random_address()
        delay_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )
        prescaler_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )

        test_prop = MomentaryDelayProperty(
            address, "test_prop", delay_prop, prescaler_prop
        )

        delay_value = randint(0, 255)
        prescaler_value = randint(0, 255)
        delay_prop.load(delay_value)
        prescaler_prop.load(prescaler_value)
        seconds = delay_value * max(1, prescaler_value) / 10

        assert test_prop.value == seconds

    def test_new_value(self):
        """Test setting a new value."""
        address = random_address()
        delay_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )
        prescaler_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )

        test_prop = MomentaryDelayProperty(
            address, "test_prop", delay_prop, prescaler_prop
        )
        delay_prop.load(0)
        prescaler_prop.load(0)
        assert test_prop.new_value is None

        # Test small number delays (< 255).  Result should be exact
        for delay_value in range(1, 255):
            test_prop.new_value = delay_value / 10
            assert test_prop.new_value == delay_value / 10
            assert delay_prop.new_value == delay_value
            assert prescaler_prop.new_value == 1

        # Test a set of larger number
        for _ in range(0, 20):
            delay_value = randint(26, 255)
            prescaler_value = randint(1, 255)
            seconds = delay_value * max(1, prescaler_value) / 10
            test_prop.new_value = seconds
            assert (
                delay_prop.new_value * prescaler_prop.new_value / 10
                == test_prop.new_value
            )

        # Test setting new_value to value
        delay_value = randint(1, 20)
        prescaler_value = 1
        new_delay_value = randint(21, 50)
        seconds = delay_value / 10
        new_seconds = new_delay_value / 10

        # Set delay in seconds to seconds
        delay_prop.load(delay_value)
        prescaler_prop.load(prescaler_value)
        assert test_prop.value == seconds

        # Set new_value to new_seconds
        test_prop.new_value = new_seconds
        assert test_prop.new_value == new_seconds
        assert delay_prop.new_value == new_delay_value

        # Set new_value to seconds and confirm new_value is None
        test_prop.new_value = seconds
        assert test_prop.new_value is None
        assert delay_prop.new_value is None

        # Test too large and too small a number
        for val in [10000, -1]:
            try:
                test_prop.new_value = val
                assert False
            except ValueError:
                assert True

    def test_load(self):
        """Test the is_loaded property."""
        address = random_address()
        delay_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )
        prescaler_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )

        test_prop = MomentaryDelayProperty(
            address, "test_prop", delay_prop, prescaler_prop
        )
        assert not test_prop.is_loaded
        delay_prop.load(0)
        assert not test_prop.is_loaded
        prescaler_prop.load(0)
        assert test_prop.is_loaded

    def test_is_dirty(self):
        """Test the id_dirty property."""
        address = random_address()
        delay_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )
        prescaler_prop = ExtendedProperty(
            address, "delay", int, False, False, PropertyType.ADVANCED
        )

        test_prop = MomentaryDelayProperty(
            address, "test_prop", delay_prop, prescaler_prop
        )
        assert not test_prop.is_dirty
        delay_prop.load(0)
        assert not test_prop.is_dirty
        prescaler_prop.load(0)
        assert not test_prop.is_dirty

        delay_prop.new_value = randint(1, 255)
        assert test_prop.is_dirty

        delay_prop.new_value = None
        assert not test_prop.is_dirty

        prescaler_prop.new_value = randint(1, 255)
        assert test_prop.is_dirty

        prescaler_prop.new_value = None
        assert not test_prop.is_dirty

        delay_prop.new_value = randint(1, 255)
        assert test_prop.is_dirty

        delay_prop.new_value = randint(1, 255)
        prescaler_prop.new_value = randint(1, 255)
        assert test_prop.is_dirty

        delay_prop.new_value = None
        prescaler_prop.new_value = None
        assert not test_prop.is_dirty
