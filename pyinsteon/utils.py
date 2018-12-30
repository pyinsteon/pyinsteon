"""Utility methods."""
from typing import Iterable



from .constants import (HC_LOOKUP,
                        UC_LOOKUP,
                        X10Commands,
                        X10CommandType)


def housecode_to_byte(housecode: str) -> int:
    """Return the byte value of an X10 housecode."""
    return HC_LOOKUP.get(housecode.lower())


def unitcode_to_byte(unitcode: int) -> int:
    """Return the byte value of an X10 unitcode."""
    return UC_LOOKUP.get(unitcode)


def byte_to_housecode(bytecode: int) -> str:
    """Return an X10 housecode value from a byte value."""
    hc = list(HC_LOOKUP.keys())[list(HC_LOOKUP.values()).index(bytecode)]
    return hc.upper()


def byte_to_unitcode(bytecode: int) -> int:
    """Return an X10 unitcode value from a byte value."""
    return list(UC_LOOKUP.keys())[list(UC_LOOKUP.values()).index(bytecode)]


def byte_to_int(bytecode: bytes) -> int:
    """Return an int from a byte string."""
    return int.from_bytes(bytecode, byteorder='big')


def x10_command_type(command: X10Commands) -> X10CommandType:
    """Return the X10 command type from an X10 command."""
    command_type = X10CommandType.DIRECT
    cmd_val = command.value if isinstance(command, X10Commands) else command
    if cmd_val in [X10Commands.ALL_UNITS_OFF.value,
                   X10Commands.ALL_LIGHTS_ON.value,
                   X10Commands.ALL_LIGHTS_OFF.value]:
        command_type = X10CommandType.BROADCAST
    return command_type


def rawX10_to_bytes(rawX10: int) -> int:
    """Return the byte value of a raw X10 command."""
    yield rawX10 >> 4
    yield rawX10 & 0x0f


def bit_is_set(bitmask: int, bit: int) -> bool:
    """Return True if a specific bit is set in a bitmask.

    Uses the low bit is 1 and the high bit is 8.
    """
    return bool(bitmask & (1 << bit))


def set_bit(bitmask:int, bit: int, is_on: bool) -> int:
    """Set the value of a bit in a bitmask on or off.

    Uses the low bit is 0 and the high bit is 7.
    """
    if is_on:
        return bitmask | (1 << bit)
    return bitmask & (0xff & ~(1 << bit))

def vars_to_bytes(vars: Iterable) -> bytes:
    """Create a byte string from a set of values."""
    from enum import Enum
    from .address import Address
    from .messages.message_flags import MessageFlags
    from .messages.user_data import UserData

    msg = bytearray()
    for val in vars:
        if val is None:
            pass
        elif isinstance(val, int):
            msg.append(val)
        elif isinstance(val, Address):
            if val.address is None:
                pass
            else:
                msg.extend(val.bytes)
        elif isinstance(val, MessageFlags):
            msg.extend(val.bytes)
        elif isinstance(val, bytearray):
            msg.extend(val)
        elif isinstance(val, bytes):
            msg.extend(val)
        elif isinstance(val, UserData):
            msg.extend(val.bytes)
        elif isinstance(val, Enum):
            msg.extend(val.value)

    return bytes(msg)
