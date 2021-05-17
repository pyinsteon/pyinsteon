"""Test operating flags and extended flags features."""

import unittest

from pyinsteon.extended_property import ExtendedProperty
from pyinsteon.operating_flag import OperatingFlag
from tests.utils import randint, random_address


class TestFlags(unittest.TestCase):
    """Test the flags classes."""

    def test_basic_bool_flag(self):
        """Test a bool writable flag."""
        ex_prop = ExtendedProperty(random_address(), "ext_prop", bool, False, False)
        op_flag = OperatingFlag(random_address(), "op_flag", bool, False, False)

        for flag in [ex_prop, op_flag]:
            assert not flag.is_loaded
            for orig in [True, False]:
                mod = not orig
                flag.load(orig)
                assert flag.is_loaded

                assert flag.value == orig
                assert not flag.is_dirty

                flag.new_value = mod
                assert flag.value == orig
                assert flag.new_value == mod
                assert flag.is_dirty

                assert not flag.is_read_only
                assert not flag.is_reversed

    def test_basic_int_flag(self):
        """Test an int writable flag."""
        ex_prop = ExtendedProperty(random_address(), "ext_prop", int, False, False)
        op_flag = OperatingFlag(random_address(), "op_flag", int, False, False)

        for flag in [ex_prop, op_flag]:
            orig = randint(0, 100)
            mod = randint(101, 255)

            assert not flag.is_loaded
            flag.load(orig)
            assert flag.is_loaded

            assert flag.value == orig
            assert not flag.is_dirty

            flag.new_value = mod
            assert flag.value == orig
            assert flag.new_value == mod
            assert flag.is_dirty

            flag.new_value = None
            assert not flag.is_dirty

            assert not flag.is_reversed
            assert not flag.is_read_only

    def test_reverse_bool_flag(self):
        """Test a reversed bool writable flag."""
        ex_prop = ExtendedProperty(random_address(), "ext_prop", bool, True, False)
        op_flag = OperatingFlag(random_address(), "op_flag", bool, True, False)

        for flag in [ex_prop, op_flag]:
            assert not flag.is_loaded
            for orig in [True, False]:
                reverse = not orig
                flag.load(orig)
                assert flag.is_loaded

                assert flag.value == reverse
                assert not flag.is_dirty

                flag.new_value = reverse
                assert flag.value == reverse
                assert flag.new_value == orig
                assert flag.is_dirty

                assert flag.is_reversed
                assert not flag.is_read_only

    def test_read_only_flag(self):
        """Test an int read only flag."""
        ex_prop = ExtendedProperty(random_address(), "ext_prop", int, False, True)
        op_flag = OperatingFlag(random_address(), "op_flag", int, False, True)

        for flag in [ex_prop, op_flag]:
            orig = randint(0, 100)
            mod = randint(101, 255)

            assert not flag.is_loaded
            flag.load(orig)
            assert flag.is_loaded

            assert flag.value == orig
            assert not flag.is_dirty

            flag.new_value = mod
            assert flag.value == orig
            assert flag.new_value is None
            assert not flag.is_dirty

            flag.new_value = None
            assert not flag.is_dirty

            assert not flag.is_reversed
            assert flag.is_read_only

    def test_is_dirty(self):
        """Test is_dirty property."""
        ex_prop = ExtendedProperty(random_address(), "ext_prop", int, False, False)
        op_flag = OperatingFlag(random_address(), "op_flag", int, False, False)

        for flag in [ex_prop, op_flag]:
            # load(orig) -> not is_dirty
            # new_value = mod -> is_dirty
            # new_value = orig => not is_dirty
            # new_value = None => not is_dirty

            orig = randint(0, 100)
            mod = randint(101, 255)

            assert not flag.is_loaded
            flag.load(orig)
            assert flag.is_loaded

            assert flag.value == orig
            assert not flag.is_dirty

            flag.new_value = mod
            assert flag.value == orig
            assert flag.new_value == mod
            assert flag.is_dirty

            flag.new_value = orig
            assert flag.value == orig
            assert flag.new_value is None
            assert not flag.is_dirty

            flag.new_value = mod
            assert flag.is_dirty
            flag.new_value = None
            assert flag.value == orig
            assert flag.new_value is None
            assert not flag.is_dirty
