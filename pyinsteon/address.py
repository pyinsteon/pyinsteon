"""Insteon device address class."""
import logging
import binascii

from .utils import byte_to_housecode, byte_to_unitcode, housecode_to_byte, unitcode_to_byte

_LOGGER = logging.getLogger(__name__)


class Address():
    """Datatype definition for INSTEON device address handling."""

    def __init__(self, addr):
        """Create an Address object."""
        self._is_x10 = False
        self._addr = self._normalize(addr)

    def __repr__(self):
        """Representation of the Address object."""
        return self.id

    def __str__(self):
        """Return the Address object as a string."""
        return self.id

    def __eq__(self, other):
        """Test for equality."""
        equals = False
        if hasattr(other, 'address'):
            equals = self._addr == other.address
        return equals

    def __ne__(self, other):
        """Test for not equals."""
        not_equals = True
        if hasattr(other, 'address'):
            not_equals = self._addr != other.address
        return not_equals

    def __lt__(self, other):
        """Test for less than."""
        if isinstance(other, Address):
            return str(self) < str(other)
        raise TypeError

    def __gt__(self, other):
        """Test for greater than."""
        if isinstance(other, Address):
            return str(self) > str(other)
        raise TypeError

    def __hash__(self):
        """Create a hash code for the Address object."""
        return hash(self.id)

    def matches_pattern(self, other):
        """Test Address object matches the pattern of another  object."""
        matches = False
        if hasattr(other, 'address'):
            if self._addr is None or other.address is None:
                matches = True
            else:
                matches = self._addr == other.address
        return matches

    def _normalize(self, addr):
        """Take any format of address and turn it into a hex string."""
        normalize = None
        if isinstance(addr, Address):
            normalize = addr.address
            self._is_x10 = addr.is_x10

        elif isinstance(addr, bytearray):
            normalize = binascii.unhexlify(binascii.hexlify(addr).decode())

        elif isinstance(addr, bytes):
            normalize = addr

        elif isinstance(addr, str):
            addr = addr.replace('.', '')
            addr = addr[0:6]
            if addr[0:3].lower() == 'x10':
                x10_addr = Address.x10(addr[3:4], int(addr[4:6]))
                normalize = x10_addr.address
                self._is_x10 = True
            else:
                normalize = binascii.unhexlify(addr.lower())

        elif addr is None:
            normalize = None

        else:
            _LOGGER.warning('Address class init with unknown type %s: %r',
                            type(addr), addr)
        return normalize

    @property
    def address(self):
        """Emit the address in raw form."""
        return self._addr

    @property
    def human(self):
        """Emit the address in human-readible format (AA.BB.CC)."""
        addrstr = '00.00.00'
        if self._addr:
            if self._is_x10:
                housecode_byte = self._addr[1]
                housecode = byte_to_housecode(housecode_byte)
                unitcode_byte = self._addr[2]
                unitcode = byte_to_unitcode(unitcode_byte)
                addrstr = 'X10.{}.{:02d}'.format(housecode.upper(), unitcode)
            else:
                addrstr = '{}.{}.{}'.format(self.hex[0:2],
                                            self.hex[2:4],
                                            self.hex[4:6]).upper()
        return addrstr

    @property
    def hex(self):
        """Emit the address in bare hex format (aabbcc)."""
        addrstr = '000000'
        if self._addr is not None:
            addrstr = binascii.hexlify(self._addr).decode()
        return addrstr

    @property
    def bytes(self):
        """Emit the address in bytes format."""
        addrbyte = b'\x00\x00\x00'
        if self._addr is not None:
            addrbyte = self._addr
        return addrbyte

    @property
    def id(self):
        """Return the ID of the device address."""
        dev_id = ''
        if self._is_x10:
            dev_id = 'x10{}{:02d}'.format(self.x10_housecode,
                                          self.x10_unitcode)
        else:
            dev_id = self.hex
        return dev_id

    @property
    def is_x10(self):
        """Test if this is an X10 address."""
        return self._is_x10

    @is_x10.setter
    def is_x10(self, val: bool):
        """Set if this is an X10 address."""
        self._is_x10 = val

    @property
    def x10_housecode_byte(self):
        """Emit the X10 house code byte value."""
        housecode = None
        if self.is_x10:
            housecode = self._addr[1]
        return housecode

    @property
    def x10_unitcode_byte(self):
        """Emit the X10 unit code byte value."""
        unitcode = None
        if self.is_x10:
            unitcode = self._addr[2]
        return unitcode

    @property
    def x10_housecode(self):
        """Emit the X10 house code."""
        housecode = None
        if self.is_x10:
            housecode = byte_to_housecode(self._addr[1])
        return housecode

    @property
    def x10_unitcode(self):
        """Emit the X10 unit code."""
        unitcode = None
        if self.is_x10:
            unitcode = byte_to_unitcode(self._addr[2])
        return unitcode

    @classmethod
    def x10(cls, housecode, unitcode):
        """Create an X10 device address."""
        if housecode.lower() in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                                 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p']:
            byte_housecode = housecode_to_byte(housecode)
        else:
            if isinstance(housecode, str):
                _LOGGER.error('X10 house code error: %s', housecode)
            else:
                _LOGGER.error('X10 house code is not a string')
            raise ValueError

        # 20, 21 and 22 for All Units Off, All Lights On and All Lights Off
        # 'fake' units
        if unitcode in range(1, 17) or unitcode in range(20, 23):
            byte_unitcode = unitcode_to_byte(unitcode)
        else:
            if isinstance(unitcode, int):
                _LOGGER.error('X10 unit code error: %d', unitcode)
            else:
                _LOGGER.error('X10 unit code is not an integer 1 - 16')
            raise ValueError

        addr = Address(bytearray([0x00, byte_housecode, byte_unitcode]))
        addr.is_x10 = True
        return addr
