"""Insteon device address class."""
import logging

from .utils import (
    byte_to_housecode,
    byte_to_unitcode,
    housecode_to_byte,
    unitcode_to_byte,
)


_LOGGER = logging.getLogger(__name__)


def create(housecode: str, unitcode: int):
    """Create an X10 device address."""
    if housecode.lower() in [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
    ]:
        byte_housecode = housecode_to_byte(housecode)
    else:
        if isinstance(housecode, str):
            str_error = "X10 house code invalid: {}".format(housecode)
        else:
            str_error = "X10 house code is not a string"
            raise ValueError(str_error)

    # 20, 21 and 22 for All Units Off, All Lights On and All Lights Off
    # 'fake' units
    if unitcode in range(1, 17) or unitcode in range(20, 23):
        byte_unitcode = unitcode_to_byte(unitcode)
    else:
        if isinstance(unitcode, int):
            str_error = "X10 unit code error: {}".format(unitcode)
        else:
            str_error = "X10 unit code is not an integer 1 - 16"
            raise ValueError(str_error)

    addr = X10Address(bytearray([byte_housecode, byte_unitcode]))
    return addr


class X10Address:
    """Datatype definition for an X10 device address."""

    def __init__(self, housecode_unitcode: bytearray):
        """Create an X10 device address."""
        if len(housecode_unitcode) != 2:
            raise ValueError("housecode_unitcode must be 2 bytes")
        self._housecode_byte = housecode_unitcode[0]
        self._unitcode_byte = housecode_unitcode[1]
        valid = self._check_housecode_unitcode()
        if not valid:
            raise ValueError("Invalid housecode or unitcode byte")

    def __repr__(self):
        """Return the string representation of an X10 device address."""
        hex_housecode = hex(self._housecode_byte)
        hex_unitcode = hex(self._unitcode_byte)
        str_rep = {"housecode": hex_housecode, "unitcode": hex_unitcode}
        return str(str_rep)

    def __str__(self):
        """Return the string representation of an X10 device address."""
        str_rep = {"housecode": self.housecode, "unitcode": self.unitcode}
        return str(str_rep)

    def __bytes__(self):
        """Return the byte representation of an X10 address."""
        return bytes(bytearray([self._housecode_byte, self._unitcode_byte]))

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
        err = "Item index must be 0 or 1: {}".format(byte)
        raise ValueError(err)

    def _check_housecode_unitcode(self):
        """Check to confirm housecode and unitcode are valid."""
        housecode = byte_to_housecode(self._housecode_byte)
        unitcode = byte_to_unitcode(self._unitcode_byte)
        if housecode and unitcode:
            return True
        return False

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
        return byte_to_housecode(self._housecode_byte)

    @property
    def unitcode(self):
        """Emit the X10 unit code."""
        return byte_to_unitcode(self._unitcode_byte)
