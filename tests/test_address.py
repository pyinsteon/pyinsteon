"""Test the Address class."""
import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from tests import set_log_levels


class TestAddress(unittest.TestCase):
    """Test the address class."""

    def setUp(self):
        """Set up the tests."""
        self.hex = "010203"
        self.address = Address(self.hex)
        self.address_bytes = Address(bytearray(unhexlify(self.hex)))
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_bytes(self):
        """Test address to bytes."""
        assert bytes(self.address) == unhexlify(self.hex)

    def test_high_mid_low(self):
        """Test high, middle and low bytes."""
        assert self.address[0] == 0x01
        assert self.address[1] == 0x02
        assert self.address[2] == 0x03
        try:
            # pylint: disable=unused-variable
            failtest = self.address[3]  # noqa: F841
            assert False
        except ValueError:
            assert True

    def test_eq(self):
        """Test equals."""
        assert self.address == Address("010203")

    def test_ne(self):
        """Test not equals."""
        assert self.address != Address("010204")

    def test_from_byte_array(self):
        """Test create from byte array."""
        assert self.address == self.address_bytes


if __name__ == "__main__":
    unittest.main()
