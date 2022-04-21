"""Test UserData data type."""

import unittest
from binascii import unhexlify

from pyinsteon.data_types.user_data import UserData, create_empty
from tests import set_log_levels


class TestUserData(unittest.TestCase):
    """Test UserData data type."""

    def setUp(self):
        """Set up the test."""
        self.hex_user_data = "0102030405060708090a0b0c0d0e"
        self.bytes_user_data = unhexlify(self.hex_user_data)
        self.user_data = UserData(unhexlify(self.hex_user_data))
        self.empty_user_data = create_empty()
        self.emtpy_none_user_data = create_empty(None)
        self.values_user_data = create_empty()
        self._data = {
            "d1": 0xB1,
            "d2": 0xB2,
            "d3": 0xB3,
            "d4": 0xB4,
            "d5": 0xB5,
            "d6": 0xB6,
            "d7": 0xB7,
            "d8": 0xB8,
            "d9": 0xB9,
            "d10": 0xBA,
            "d11": 0xBB,
            "d12": 0xBC,
            "d13": 0xBD,
            "d14": 0xBE,
        }
        self.dict_user_data = UserData(self._data)
        for itm in range(1, 15):
            key = "d{}".format(itm)
            self.values_user_data[key] = itm + 0xA0
        set_log_levels(
            logger="info",
            logger_pyinsteon="info",
            logger_messages="info",
            logger_topics=False,
        )

    def test_user_data_items(self):
        """Test each UserData item for proper mapping."""
        for itm in range(1, 15):
            key = "d{}".format(itm)
            assert self.user_data[key] == itm

    def test_user_data_bytes(self):
        """Test the bytes representation of UserData."""
        assert bytes(self.user_data) == self.bytes_user_data

    def test_empty(self):
        """Test creating an empty UserData element."""
        for itm in range(1, 15):
            key = "d{}".format(itm)
            assert self.empty_user_data[key] == 0x00

    def test_empty_none(self):
        """Test creating an empty Userdata element set to None."""
        for itm in range(1, 15):
            key = "d{}".format(itm)
            assert self.emtpy_none_user_data[key] is None

    def test_set_value(self):
        """Test setting UserData values."""
        for itm in range(1, 15):
            key = "d{}".format(itm)
            assert self.values_user_data[key] == itm + 0xA0

    def test_from_dict(self):
        """Test create from dict."""
        for itm in range(1, 15):
            key = "d{}".format(itm)
            assert self.dict_user_data[key] == (itm + 0xB0)


if __name__ == "__main__":
    unittest.main()
