"""Test the ramp rate in seconds property."""
from unittest import TestCase

from pyinsteon.config.extended_property import ExtendedProperty
from pyinsteon.config.ramp_rate import RampRateProperty
from pyinsteon.constants import PropertyType, RampRate
from pyinsteon.utils import ramp_rate_to_seconds, seconds_to_ramp_rate

from ..utils import random_address


class TestRampRateProperty(TestCase):
    """Test the ramp rate flag."""

    def test_value(self):
        """Test the ramp rate value."""
        address = random_address()
        ramp_rate_prop = ExtendedProperty(
            address, "ramp_rate", RampRate, False, False, PropertyType.ADVANCED
        )
        test_prop = RampRateProperty(address, "test_prop", ramp_rate_prop)

        assert ramp_rate_prop.value is None
        test_prop.value is None
        ramp_rate_prop.load(RampRate.MIN_4)
        assert test_prop.value == ramp_rate_to_seconds(RampRate.MIN_4)

    def test_new_value(self):
        """Test the new_value property."""

        address = random_address()
        ramp_rate_prop = ExtendedProperty(
            address, "ramp_rate", RampRate, False, False, PropertyType.ADVANCED
        )
        test_prop = RampRateProperty(address, "test_prop", ramp_rate_prop)
        assert ramp_rate_prop.new_value is None
        assert test_prop.new_value is None

        # Test all ramp rates except 0 and 2
        for value in range(1, 0x1F):
            if value == 2:  # Special condition
                continue
            ramp_rate = RampRate(value)
            seconds = ramp_rate_to_seconds(ramp_rate)
            test_prop.new_value = seconds
            assert ramp_rate_prop.new_value == ramp_rate
            assert test_prop.new_value == seconds

        # Test 0 and 2
        for value in [0, 2]:
            seconds = ramp_rate_to_seconds(value)
            test_prop.new_value = seconds
            assert ramp_rate_prop.new_value == seconds_to_ramp_rate(seconds)

        # Test clearing the changes
        test_prop.new_value = None
        assert ramp_rate_prop.new_value is None

        test_prop.new_value = 3
        ramp_rate_prop.new_value = None
        assert test_prop.new_value is None

        # Test putting new_value to current value
        seconds = ramp_rate_to_seconds(RampRate.SEC_0_3)
        ramp_rate_prop.load(RampRate.SEC_0_3)
        assert test_prop.value == seconds
        seconds2 = seconds + 2
        ramp_rate2 = seconds_to_ramp_rate(seconds2)
        test_prop.new_value = seconds2
        assert ramp_rate_prop.new_value == ramp_rate2
        assert test_prop.new_value == ramp_rate_to_seconds(ramp_rate2)
        test_prop.new_value = test_prop.value
        assert test_prop.new_value is None
        assert ramp_rate_prop.new_value is None

    def test_is_dirty(self):
        """Test the is_dirty property."""

        address = random_address()
        ramp_rate_prop = ExtendedProperty(
            address, "ramp_rate", RampRate, False, False, PropertyType.ADVANCED
        )
        test_prop = RampRateProperty(address, "test_prop", ramp_rate_prop)

        assert not ramp_rate_prop.is_dirty
        assert not test_prop.is_dirty
        ramp_rate_prop.load(0)
        assert not ramp_rate_prop.is_dirty
        assert not test_prop.is_dirty
        ramp_rate_prop.new_value = RampRate.MIN_1
        assert ramp_rate_prop.is_dirty
        assert test_prop.is_dirty
        ramp_rate_prop.new_value = None
        assert not ramp_rate_prop.is_dirty
        assert not test_prop.is_dirty
        ramp_rate_prop.new_value = RampRate.MIN_1_5
        assert ramp_rate_prop.is_dirty
        assert test_prop.is_dirty
        ramp_rate_prop.new_value = ramp_rate_prop.value
        assert not ramp_rate_prop.is_dirty
        assert not test_prop.is_dirty

    def test_is_loaded(self):
        """Test the is_dirty property."""

        address = random_address()
        ramp_rate_prop = ExtendedProperty(
            address, "ramp_rate", RampRate, False, False, PropertyType.ADVANCED
        )
        test_prop = RampRateProperty(address, "test_prop", ramp_rate_prop)

        assert not ramp_rate_prop.is_loaded
        assert not test_prop.is_loaded

        ramp_rate_prop.load(RampRate.MIN_1)
        assert ramp_rate_prop.is_loaded
        assert test_prop.is_loaded
