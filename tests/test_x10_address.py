from binascii import unhexlify
import logging
import unittest
import sys

from pyinsteon.x10_address import X10Address, create

_LOGGER = logging.getLogger(__name__)
_INSTEON_LOGGER = logging.getLogger('pyinsteon')


class TestX10Address(unittest.TestCase):

    def setUp(self):
        self.housecode = 'C'
        self.housecode_byte = 0x02
        self.unitcode = 6
        self.unitcode_byte = 0x09
        self.address = X10Address(bytearray([self.housecode_byte,
                                             self.unitcode_byte]))
        self.address_create = create(self.housecode, self.unitcode)
        
        # _LOGGER.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(sys.stdout)
        _LOGGER.addHandler(stream_handler)

    def test_bytes(self):
        byte_out = bytes(bytearray([self.housecode_byte, 
                                    self.unitcode_byte]))
        assert bytes(self.address) == byte_out

    def test_getitem(self):
        assert self.address[0] == self.housecode_byte
        assert self.address[1] == self.unitcode_byte
        try:
            fail_test = self.address[2]
            assert False
        except ValueError:
            assert True

    def test_eq(self):
        assert self.address == X10Address(bytearray([0x02, 0x09]))

    def test_ne(self):
        assert self.address != X10Address(bytearray([0x01, 0x09]))

    def test_create(self):
        test_bytes = bytes(bytearray([self.housecode_byte, self.unitcode_byte]))
        assert bytes(self.address_create) == test_bytes


if __name__ == '__main__':
    unittest.main()