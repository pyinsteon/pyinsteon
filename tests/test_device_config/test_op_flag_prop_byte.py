"""Test the OpFlagPropertyByte class."""
from random import randint
from unittest import TestCase

from pyinsteon.config.op_flag_property_byte import OpFlagPropertyByte
from pyinsteon.config.operating_flag import OperatingFlag
from pyinsteon.utils import bit_is_set, set_bit

from ..utils import random_address


class TestOpFlagPropertyByte(TestCase):
    """Test the OpFlagPropertyByte class."""

    def setUp(self) -> None:
        """Set up the tests."""
        address = random_address()
        flag0 = OperatingFlag(address=address, name="byte0", value_type=bool)
        # No bit 1 flag exists
        flag2 = OperatingFlag(address=address, name="byte2", value_type=bool)
        flag3 = OperatingFlag(address=address, name="byte3", value_type=bool)
        flag4 = OperatingFlag(address=address, name="byte4", value_type=bool)
        flag5 = OperatingFlag(address=address, name="byte5", value_type=bool)
        flag6 = OperatingFlag(address=address, name="byte6", value_type=bool)
        flag7 = OperatingFlag(address=address, name="byte7", value_type=bool)
        self.flags = {
            0: flag0,
            2: flag2,
            3: flag3,
            4: flag4,
            5: flag5,
            6: flag6,
            7: flag7,
        }
        self.prop_byte = OpFlagPropertyByte(
            address=address, name="prop_byte", flags=self.flags
        )

    def test_flag_to_byte(self):
        """Test converting a set of flags to a byte."""
        for _ in range(0, 20):
            value = randint(1, 255)
            value = set_bit(value, 1, False)
            for bit, flag in self.flags.items():
                bit_value = bit_is_set(value, bit)
                flag.set_value(bit_value)
            assert self.prop_byte.value == value

    def test_byte_to_flag(self):
        """Test converting a byte to a set of flags."""
        for _ in range(0, 20):
            value = randint(1, 255)
            self.prop_byte.set_value(value)
            for bit, flag in self.flags.items():
                assert flag.value == bit_is_set(value, bit)

        # if set_value(None) all flags should be set to value = None
        self.prop_byte.set_value(None)
        for _, flag in self.flags.items():
            assert not flag.value

    def test_new_value_to_byte(self):
        """Test setting a new value to a byte value."""
        # If values are not loaded new_value is None
        assert self.prop_byte.new_value is None
        init_value = randint(1, 255)
        init_bit_1 = bit_is_set(init_value, 1)
        self.prop_byte.set_value(init_value)
        for _ in range(0, 20):
            new_value = randint(1, 255)
            for bit, flag in self.flags.items():
                flag.new_value = bit_is_set(new_value, bit)
            assert self.prop_byte.new_value == set_bit(new_value, 1, init_bit_1)

    def test_missing_ops_flag(self):
        """Test when one bit has no associated operating flag."""

        prop_byte = OpFlagPropertyByte(
            address=random_address(), name="prop_byte", flags=self.flags
        )

        # Test that a missing bit loads and is represented in the output
        init_value = randint(1, 255)
        init_value = set_bit(init_value, 1, True)
        prop_byte.set_value(init_value)
        assert bit_is_set(prop_byte.value, 1)

        # Test that a missing bit never changes even if new_value changes it
        new_value = set_bit(init_value, 1, False)
        assert new_value != init_value
        prop_byte.new_value = new_value
        assert bit_is_set(prop_byte.new_value, 1)

    def test_is_dirty(self):
        """Test the is_dirty property."""

        # Test if any one flag is dirty should result in is_dirty
        assert not self.prop_byte.is_dirty
        for _, flag in self.flags.items():
            flag.new_value = not flag.value
            assert self.prop_byte.is_dirty
            flag.new_value = None
            assert not self.prop_byte.is_dirty

    def test_is_loaded(self):
        """Test the is_loaded property."""
        # Test each flag to ensure is_loaded is False
        for _, flag in self.flags.items():
            assert not flag.is_loaded

        # Set one flag at a time and ensure is_loaded is still False
        flag_bit = list(self.flags)
        for bit in flag_bit:
            flag = self.flags[bit]
            assert not flag.is_loaded
            assert self.prop_byte.value is None
            flag.set_value(0)
            assert flag.is_loaded
            assert self.prop_byte.is_loaded == (bit == flag_bit[-1])

    def test_value(self):
        """Test the flag value calculation."""
        # Run test 8 times to be sure it is random
        for _ in range(0, 8):
            test_value = 0
            for bit, flag in self.flags.items():
                bit_value = randint(0, 1)
                flag.set_value(bit_value)
                test_value = set_bit(test_value, bit, bit_value)
            assert self.prop_byte.value == test_value
