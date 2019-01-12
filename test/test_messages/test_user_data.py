"""Test UserData data type."""
from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.messages.user_data import UserData, create_empty


_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestUserData(unittest.TestCase):

    def setUp(self):
        self.hex_userdata = '0102030405060708090a0b0c0d0e'
        self.bytes_userdata = unhexlify(self.hex_userdata)
        self.userdata = UserData(unhexlify(self.hex_userdata))
        self.empty_userdata = create_empty()
        self.emtpy_none_userdata = create_empty(None)
        self.values_userdata = create_empty()
        self.dict_userdata = UserData({'d1': 0xb1,
                                       'd2': 0xb2,
                                       'd3': 0xb3,
                                       'd4': 0xb4,
                                       'd5': 0xb5,
                                       'd6': 0xb6,
                                       'd7': 0xb7,
                                       'd8': 0xb8,
                                       'd9': 0xb9,
                                       'd10': 0xba,
                                       'd11': 0xbb,
                                       'd12': 0xbc,
                                       'd13': 0xbd,
                                       'd14': 0xbe})
        for itm in range(1, 15):
            key = 'd{}'.format(itm)
            self.values_userdata[key] = itm + 0xa0
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)
        _LOGGER.setLevel(logging.DEBUG)

    def test_userdata_items(self):
        """Test each UserData item for proper mapping."""
        for itm in range(1, 15):
            key = 'd{}'.format(itm)
            assert self.userdata[key] == itm

    def test_userdata_bytes(self):
        """Test the bytes representation of UserData."""
        assert bytes(self.userdata) == self.bytes_userdata

    def test_empty(self):
        """Test creating an empty UserData element."""
        for itm in range(1, 15):
            key = 'd{}'.format(itm)
            assert self.empty_userdata[key] == 0x00

    def test_empty_none(self):
        """Test creating an empty Userdata element set to None."""
        for itm in range(1, 15):
            key = 'd{}'.format(itm)
            assert self.emtpy_none_userdata[key] == None

    def test_set_value(self):
        """Test setting UserData values."""
        for itm in range(1, 15):
            key = 'd{}'.format(itm)
            assert self.values_userdata[key] == itm + 0xa0

    def test_from_dict(self):
        """Test create from dict."""
        for itm in range(1, 15):
            key = 'd{}'.format(itm)
            assert self.dict_userdata[key] == (itm + 0xb0)


if __name__ == '__main__':
    unittest.main()