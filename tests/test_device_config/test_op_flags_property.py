"""Test operating flags and extended flags features."""
import random
import unittest

from pyinsteon.config.extended_property import ExtendedProperty
from pyinsteon.config.op_flag_property import OpFlagProperty
from pyinsteon.utils import bit_is_set
from tests.utils import random_address


class TestOpsFlagsProperty(unittest.TestCase):
    """Test the flags classes."""

    def test_op_flag_property(self):
        """Test a bool writable flag."""
        addr = random_address()
        ex_prop = ExtendedProperty(addr, "ext_prop", int, False, False)
        op_flags = {
            0: OpFlagProperty(addr, "op_flag_0", ex_prop, 0),
            1: OpFlagProperty(addr, "op_flag_1", ex_prop, 1),
            2: OpFlagProperty(addr, "op_flag_2", ex_prop, 2),
            3: OpFlagProperty(addr, "op_flag_7", ex_prop, 3),
            4: OpFlagProperty(addr, "op_flag_3", ex_prop, 4),
            5: OpFlagProperty(addr, "op_flag_4", ex_prop, 5),
            6: OpFlagProperty(addr, "op_flag_5", ex_prop, 6),
            7: OpFlagProperty(addr, "op_flag_6", ex_prop, 7),
        }

        assert not op_flags[0].is_loaded
        assert op_flags[0].value is None
        assert op_flags[0].new_value is None

        ex_prop_value = random.randint(0, 255)
        ex_prop_new_value = random.randint(0, 255)
        ex_prop.load(ex_prop_value)

        for bit, flag in op_flags.items():
            is_set = bit_is_set(ex_prop_value, bit)
            assert flag.value == is_set
            assert not flag.is_dirty
            assert flag.is_loaded

        ex_prop.new_value = ex_prop_new_value

        for bit, flag in op_flags.items():
            is_set = bit_is_set(ex_prop_value, bit)
            new_val_is_set = bit_is_set(ex_prop_new_value, bit)
            assert flag.is_dirty == (is_set != new_val_is_set)
            if flag.is_dirty:
                assert flag.value != flag.new_value

        ex_prop.load(0)
        for bit, flag in op_flags.items():
            flag.new_value = True
            assert flag.is_dirty
            assert ex_prop.is_dirty
            flag.new_value = None
            assert not flag.is_dirty
            assert not ex_prop.is_dirty
