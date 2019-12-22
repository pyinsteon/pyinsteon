import unittest
from binascii import unhexlify

from pyinsteon.address import Address
from tests import set_log_levels


class TestAddress(unittest.TestCase):
    def setUp(self):
        self.hex = "010203"
        self.address = Address(self.hex)
        self.address_bytes = Address(bytearray(unhexlify(self.hex)))
        set_log_levels(
            logger="debug",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_bytes(self):
        assert bytes(self.address) == unhexlify(self.hex)

    def test_high_mid_low(self):
        assert self.address[0] == 0x01
        assert self.address[1] == 0x02
        assert self.address[2] == 0x03
        try:
            # pylint: disable=unused-variable
            failtest = self.address[3]
            assert False
        except ValueError:
            assert True

    def test_eq(self):
        assert self.address == Address("010203")

    def test_ne(self):
        assert self.address != Address("010204")

    def test_from_byte_array(self):
        assert self.address == self.address_bytes


if __name__ == "__main__":
    unittest.main()
