"""Test X10 address."""
import unittest

from pyinsteon.x10_address import X10Address, create
from tests import set_log_levels


class TestX10Address(unittest.TestCase):
    """Test X10 address."""

    def setUp(self):
        """Set up the test."""
        self.housecode = "C"
        self.housecode_byte = 0x02
        self.unitcode = 6
        self.unitcode_byte = 0x09
        self.address = X10Address((self.housecode_byte << 4) + self.unitcode_byte)
        self.address_create = create(self.housecode, self.unitcode)
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_bytes(self):
        """Test byte conversion."""
        byte_out = bytes(bytearray([(self.housecode_byte << 4) + self.unitcode_byte]))
        assert bytes(self.address) == byte_out

    def test_id(self):
        """Test the X10 address id."""
        assert self.address.id == "x10c06"

    def test_string(self):
        """Test the X10 address as string."""
        assert str(self.address) == "X10.C.06"

    def test_getitem(self):
        """Test get houscode and unit code."""
        assert self.address[0] == self.housecode_byte
        assert self.address[1] == self.unitcode_byte
        try:
            # pylint: disable=unused-variable
            fail_test = self.address[2]  # noqa: F841
            assert False
        except ValueError:
            assert True

    def test_eq(self):
        """Test equals."""
        assert self.address == X10Address((0x02 << 4) + 0x09)

    def test_ne(self):
        """Test not equals."""
        assert self.address != X10Address((0x01 << 4) + 0x09)

    def test_create(self):
        """Test create from unitcode and housecode."""
        test_bytes = bytes(bytearray([(self.housecode_byte << 4) + self.unitcode_byte]))
        assert bytes(self.address_create) == test_bytes

    def test_from_string(self):
        """Test create from string."""
        addr = X10Address("X10.A.02")
        assert bytes(addr) == b"n"

    def test_for_all_units_lights_on_off(self):
        """Test creating an X10 address for use in the All Lights and All Units on off commands."""
        addr = create("a", 0)
        assert isinstance(addr, X10Address)


if __name__ == "__main__":
    unittest.main()
