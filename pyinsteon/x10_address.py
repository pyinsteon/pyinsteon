"""Insteon device address class."""
import logging

from .constants import HC_LOOKUP
from .utils import (
    byte_to_housecode,
    byte_to_unitcode,
    housecode_to_byte,
    unitcode_to_byte,
)

_LOGGER = logging.getLogger(__name__)


def _normalize(addr):
    """Take any format of address and turn it into a byte."""

    def to_housecode_unitcode(hc_uc_byte):
        """Convert a byte value to a housecode and unitcode."""
        hc_uc = int.from_bytes(hc_uc_byte, byteorder="big")
        housecode = hc_uc >> 4
        unitcode = hc_uc & 0x0F
        return housecode, unitcode

    if isinstance(addr, X10Address):
        return addr.housecode_byte, addr.unitcode_byte

    if isinstance(addr, (bytearray, bytes)):
        return to_housecode_unitcode(bytes(addr))

    if isinstance(addr, int):
        return to_housecode_unitcode(bytes([addr]))

    if isinstance(addr, str):
        addr_clean = addr.replace(".", "").lower()
        if len(addr_clean) == 6:
            housecode = housecode_to_byte(addr_clean[3])
            unitcode = unitcode_to_byte(int(addr_clean[4:]))
            return housecode, unitcode
    raise ValueError(f"Improper X10 address: {addr}")


def create(housecode: str, unitcode: int):
    """Create an X10 device address."""
    if housecode.lower() in HC_LOOKUP:
        byte_housecode = housecode_to_byte(housecode)
    else:
        if isinstance(housecode, str):
            str_error = f"X10 house code invalid: {housecode}"
        else:
            str_error = "X10 house code is not a string"
            raise ValueError(str_error)

    # 20, 21 and 22 for All Units Off, All Lights On and All Lights Off
    # 'fake' units
    if unitcode in range(1, 17):
        byte_unitcode = unitcode_to_byte(unitcode)
    elif unitcode == 0:
        byte_unitcode = 0x00
    else:
        if isinstance(unitcode, int):
            str_error = f"X10 unit code error: {unitcode}"
        else:
            str_error = "X10 unit code is not an integer 1 - 16"
            raise ValueError(str_error)

    addr = X10Address((byte_housecode << 4) + byte_unitcode)
    return addr


class X10Address:
    """Datatype definition for an X10 device address."""

    def __init__(self, housecode_unitcode: (bytes, bytearray, str, int)):
        """Create an X10 device address."""
        housecode, unitcode = _normalize(housecode_unitcode)
        self._housecode_byte = housecode
        self._unitcode_byte = unitcode
        if not self._check_housecode_unitcode():
            raise ValueError("Invalid housecode or unitcode byte")

    def __repr__(self):
        """Return the string representation of an X10 device address."""
        housecode = byte_to_housecode(self._housecode_byte).lower()
        unitcode = byte_to_unitcode(self._unitcode_byte)
        return f"x10{housecode}{unitcode:02d}"

    def __str__(self):
        """Return the string representation of an X10 device address."""
        str_rep = f"X10.{self.housecode}.{self.unitcode:02d}"
        return str(str_rep)

    def __bytes__(self):
        """Return the byte representation of an X10 address."""
        int_value = (self._housecode_byte << 4) + self._unitcode_byte
        return bytes(bytearray([int_value]))

    def __eq__(self, other):
        """Test if two X10 addresses are equal."""
        if isinstance(other, X10Address):
            return bytes(self) == bytes(other)
        return False

    def __getitem__(self, byte):
        """Return the housecode or unitcode bytes."""
        if byte == 0:
            return self.housecode_byte
        if byte == 1:
            return self.unitcode_byte
        err = f"Item index must be 0 or 1: {byte}"
        raise ValueError(err)

    def __hash__(self):
        """Return a hash of the address."""
        return hash(str)

    def _check_housecode_unitcode(self):
        """Check to confirm housecode and unitcode are valid."""
        housecode = byte_to_housecode(self._housecode_byte)
        unitcode = byte_to_unitcode(self._unitcode_byte)
        if housecode and unitcode:
            return True
        return False

    @property
    def id(self):
        """Return the ID of the X10 address."""
        return repr(self)

    @property
    def housecode_byte(self):
        """Emit the X10 house code byte value."""
        return self._housecode_byte

    @property
    def unitcode_byte(self):
        """Emit the X10 unit code byte value."""
        return self._unitcode_byte

    @property
    def housecode(self):
        """Emit the X10 house code."""
        return byte_to_housecode(self._housecode_byte).upper()

    @property
    def unitcode(self):
        """Emit the X10 unit code."""
        return byte_to_unitcode(self._unitcode_byte)
