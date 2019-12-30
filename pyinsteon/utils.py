"""Utility methods."""
from typing import Iterable

from .address import Address
from .constants import (
    HC_LOOKUP,
    UC_LOOKUP,
    X10Commands,
    ResponseStatus,
    MessageFlagType,
)
from .protocol.commands import commands


def housecode_to_byte(housecode: str) -> int:
    """Return the byte value of an X10 housecode."""
    return HC_LOOKUP.get(housecode.lower())


def unitcode_to_byte(unitcode: int) -> int:
    """Return the byte value of an X10 unitcode."""
    return UC_LOOKUP.get(unitcode)


def byte_to_housecode(bytecode: int) -> str:
    """Return an X10 housecode value from a byte value."""
    house_code = list(HC_LOOKUP.keys())[list(HC_LOOKUP.values()).index(bytecode)]
    return house_code.upper()


def byte_to_unitcode(bytecode: int) -> int:
    """Return an X10 unitcode value from a byte value."""
    return list(UC_LOOKUP.keys())[list(UC_LOOKUP.values()).index(bytecode)]


def byte_to_command(bytecode: int) -> int:
    """Return an X10 unitcode value from a byte value."""
    cmd = byte_to_int(bytecode)
    return X10Commands(cmd)


def parse_x10(raw_x10):
    """Convert an X10 message to a dictionary."""
    housecode, uc_or_cmd = raw_x10_to_bytes(raw_x10)
    return byte_to_housecode(housecode), uc_or_cmd


def byte_to_int(bytecode: bytes) -> int:
    """Return an int from a byte string."""
    return int.from_bytes(bytecode, byteorder="big")


def raw_x10_to_bytes(raw_x10: int) -> int:
    """Return the byte value of a raw X10 command."""
    return raw_x10 >> 4, raw_x10 & 0x0F


def bit_is_set(bitmask: int, bit: int) -> bool:
    """Return True if a specific bit is set in a bitmask.

    Uses the low bit is 1 and the high bit is 8.
    """
    return bool(bitmask & (1 << bit))


def set_bit(data: int, bit: int, is_on: bool) -> int:
    """Set the value of a bit in a bitmask on or off.

    Uses the low bit is 0 and the high bit is 7.
    """
    if isinstance(data, bytes):
        bitmask = int.from_bytes(data, byteorder="big")
    else:
        bitmask = data
    if is_on:
        return bitmask | (1 << bit)
    return bitmask & (0xFF & ~(1 << bit))


def vars_to_bytes(vals: Iterable) -> bytes:
    """Create a byte string from a set of values."""
    msg = bytearray()
    for val in vals:
        if val is None:
            pass
        elif isinstance(val, (int, bytes)):
            msg.extend(bytes([val]))
        else:
            msg.extend(bytes(val))
    return bytes(msg)


def vars_to_string(vals: Iterable) -> str:
    """Create a byte string from a set of values."""
    from enum import Enum, IntEnum

    output = []
    for fld, val in vals:
        if val is None:
            pass
        elif isinstance(val, (Enum, IntEnum)):
            valstr = str(val)
        elif isinstance(val, (int, bytes)):
            valstr = "0x{0:02x}".format(val)
        else:
            valstr = str(val)
        output.append("{}: {}".format(fld, valstr))
    return ", ".join(output)


def vars_to_repr(vals: Iterable) -> str:
    """Create a byte string from a set of values."""
    from enum import Enum, IntEnum

    output = []
    for fld, val in vals:
        if val is None:
            pass
        elif isinstance(val, (Enum, IntEnum)):
            valstr = repr(val)
        elif isinstance(val, (int, bytes)):
            valstr = "0x{0:02x}".format(val)
        else:
            valstr = repr(val)
        output.append("{}: {}".format(fld, valstr))
    return ", ".join(output)


def test_values_eq(val1, val2) -> bool:
    """Test if val1 eq val2 for template management."""
    if val1 is None or val2 is None:
        return True
    if val1 == val2:
        return True
    return False


def _include_address(prefix, topic, address, message_type):
    """Test if we should include the address in the topic build."""
    if address is None:
        return False

    if isinstance(message_type, str):
        message_type = getattr(MessageFlagType, str(message_type).upper())

    if prefix == "send" and message_type == MessageFlagType.DIRECT:
        return False

    # if message_type in [MessageFlagType.ALL_LINK_CLEANUP,
    #                     MessageFlagType.DIRECT_ACK,
    #                     MessageFlagType.DIRECT_NAK]:
    #     return False

    if commands.get(topic) is None:
        return False

    return True


def _include_group(topic, group, message_type):
    if group is None:
        return False

    if not commands.use_group(topic):
        return False

    if message_type in [MessageFlagType.ALL_LINK_CLEANUP]:
        return False

    return True


def build_topic(topic, prefix=None, address=None, group=None, message_type=None):
    """Build a full topic from components."""
    full_topic = ""
    if prefix is not None:
        # Adding the . separator since there must be something after a prefix
        full_topic = "{}.".format(str(prefix))

    if _include_address(prefix, topic, address, message_type):
        addr = address.id if isinstance(address, Address) else address
        full_topic = "{}{}.".format(full_topic, addr)
        if commands.use_group(topic) and group is not None:
            group = group if group else 1
            full_topic = "{}{}.".format(full_topic, group)

    full_topic = "{}{}".format(full_topic, topic)
    if message_type is not None:
        full_topic = "{}.{}".format(full_topic, str(message_type))
    return full_topic


def multiple_status(*args):
    """Return the proper status based on the worst case of all status responses."""
    worst_response = 1
    for response in args:
        if response is None:
            continue
        if int(response) == 0 or worst_response == 0:
            worst_response = 0
        elif int(response) > worst_response:
            worst_response = int(response)
    return ResponseStatus(worst_response)
