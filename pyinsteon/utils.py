"""Utility methods."""
from functools import partial
import logging
from enum import Enum, IntEnum
import traceback
from typing import Iterable

from . import pub
from .address import Address
from .constants import (
    HC_LOOKUP,
    RAMP_RATES,
    RAMP_RATES_SEC,
    UC_LOOKUP,
    MessageFlagType,
    ResponseStatus,
    X10Commands,
    ThermostatMode,
    FanSpeedRange,
    FanSpeed,
)
from .protocol.commands import commands

_LOGGER = logging.getLogger(__name__)
_LOGGER_TOPICS = logging.getLogger("pyinsteon.topics")


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
    return X10Commands(bytecode)


def parse_x10(raw_x10):
    """Convert an X10 message to a dictionary."""
    housecode, uc_or_cmd = raw_x10_to_bytes(raw_x10)
    return byte_to_housecode(housecode), uc_or_cmd


def byte_to_int(bytecode: bytes) -> int:
    """Return an int from a byte string."""
    return int.from_bytes(bytecode, byteorder="big")


def raw_x10_to_bytes(raw_x10: int) -> int:
    """Return the byte value of a raw X10 command."""
    house_code_byte = raw_x10 >> 4
    uc_or_cmd_byte = raw_x10 & 0x0F
    return house_code_byte, uc_or_cmd_byte


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
        elif isinstance(val, int):
            msg.extend(bytes([val]))
        else:
            msg.extend(bytes(val))
    return bytes(msg)


def vars_to_string(vals: Iterable) -> str:
    """Create a byte string from a set of values."""

    output = []
    for fld, val in vals:
        if val is None:
            pass
        elif isinstance(val, (Enum, IntEnum)):
            valstr = str(val)
        elif isinstance(val, int):
            valstr = "0x{0:02x}".format(val)
        elif isinstance(val, bytes):
            valstr = "0x{:s}".format(val.hex())
        else:
            valstr = str(val)
        output.append("{}: {}".format(fld, valstr))
    return ", ".join(output)


def vars_to_repr(vals: Iterable) -> str:
    """Create a byte string from a set of values."""
    output = []
    for fld, val in vals:
        if val is None:
            pass
        elif isinstance(val, (Enum, IntEnum)):
            valstr = repr(val)
        elif isinstance(val, int):
            valstr = "0x{0:02x}".format(val)
        elif isinstance(val, bytes):
            valstr = "0x{:s}".format(val.hex())
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


def ramp_rate_to_seconds(ramp_rate: int):
    """Return the seconds associated with a ramp rate."""
    if int(ramp_rate) not in range(0, 31):
        raise ValueError("Ramp rate must be between 0x00 and 0x1f (31)")

    return RAMP_RATES[int(ramp_rate)]


def _abs_diff(list_value, test_value):
    """Return the absolute difference between two numbers."""
    return abs(list_value - test_value)


def seconds_to_ramp_rate(seconds: float):
    """Return the ramp rate asscociated with a number of seconds."""

    if seconds > 480 or seconds < 0.1:
        raise ValueError(
            "Ramp rate cannot be less than 0.1 seconds or more than 480 seconds (8 minutes)"
        )

    rr_sec_list = list(map(float, RAMP_RATES_SEC.keys()))
    abs_diff = partial(_abs_diff, test_value=seconds)
    rr_sec = min(rr_sec_list, key=abs_diff)

    return RAMP_RATES_SEC[rr_sec]


def log_error(msg, ex, topic=None, kwargs=None):
    """Print an error message when a topic cannot be distributed."""
    _LOGGER.error("An issue occured distributing the following message")
    _LOGGER.error("MSG: %s", msg)
    _LOGGER.error("Topic: %s data: %s", topic, kwargs)
    _LOGGER.error("Error: %s", str(ex))
    _LOGGER_TOPICS.debug(traceback.format_exc())
    if topic is not None:
        topic_mgr = pub.getDefaultTopicMgr()
        topic = topic_mgr.getTopic(topic, okIfNone=True)
        if topic:
            for subscriber in topic.getListeners():
                _LOGGER.error("    Subscriber: %s", subscriber)


def to_celsius(fahrenheit):
    """Convert fahrenheit to celsius."""
    return int(round((fahrenheit - 32) * 5 / 9, 0))


def to_fahrenheit(celsius):
    """Convert celsius to fahrenheit."""
    return int(round(celsius * 9 / 5 + 32, 0))


def calc_thermostat_temp(high_byte, low_byte):
    """Calculate the temperature."""
    return (low_byte | (high_byte << 8)) * 0.1


def calc_thermostat_mode(mode_byte, sys_mode_map=None, sys_low=True):
    """Calculate the system and fan mode."""
    if sys_mode_map is None:
        sys_mode_map = {
            int(ThermostatMode.OFF): ThermostatMode.OFF,
            int(ThermostatMode.AUTO): ThermostatMode.AUTO,
            int(ThermostatMode.HEAT): ThermostatMode.HEAT,
            int(ThermostatMode.COOL): ThermostatMode.COOL,
        }

    mode1 = mode_byte & 0x0F
    mode2 = mode_byte >> 4
    system_mode, fan_mode = (mode1, mode2) if sys_low else (mode2, mode1)
    if fan_mode in (0, 4):
        fan_mode = ThermostatMode.FAN_AUTO
    else:
        fan_mode = ThermostatMode.FAN_ALWAYS_ON
    sys_mode = sys_mode_map.get(system_mode)
    if sys_mode is None:
        sys_mode = ThermostatMode.AUTO
    return sys_mode, fan_mode


def publish_topic(topic, logger=None, **kwargs):
    """Publish a topic and log errors."""
    # Send log message as caller not utils.
    if logger is None:
        logger = logging.getLogger(__name__)
    try:
        pub.sendMessage(topic, **kwargs)
    except pub.ExcHandlerError as exc:
        logger.error("pubsub ExcHandlerError")
        logger.error("Error processing topic: %s", topic)
        logger.error("Error in topic listner: %s", exc.badExcListenerID)
    except pub.SenderMissingReqdMsgDataError as exc:
        logger.error("SenderMissingReqdMsgDataError")
        logger.error(str(exc))
        for listner in pub.getDefaultTopicMgr().getTopic(topic).getListeners():
            logger.error("Topic listener: %s", listner)
    except pub.SenderUnknownMsgDataError as exc:
        logger.error("SenderUnknownMsgDataError")
        logger.error(str(exc))
        for listner in pub.getDefaultTopicMgr().getTopic(topic).getListeners():
            logger.error("Topic listener: %s", listner)


def subscribe_topic(listener, topic_name, logger=None):
    """Subscribe a listener to a topic and log errors."""
    topic_mgr = pub.getDefaultTopicMgr()
    topic = topic_mgr.getOrCreateTopic(topic_name)
    if pub.isSubscribed(listener, topicName=topic.name):
        return
    if logger is None:
        logger = logging.getLogger(__name__)
    try:
        pub.subscribe(listener, topic.name)
    except pub.ListenerMismatchError as exc:
        logger.error("ListenerMismatchError")
        logger.error("args: %s", exc.args)
        logger.error("msg: %s", exc.msg)
        logger.error("module: %s", exc.module)
        logger.error("idStr: %s", exc.idStr)
        for topic_listner in pub.getDefaultTopicMgr().getTopic(topic).getListeners():
            logger.error("Topic listener: %s", topic_listner)


def unsubscribe_topic(listener, topic_name):
    """Unsubscribe a listener to a topic and log errors."""
    topic_mgr = pub.getDefaultTopicMgr()
    topic = topic_mgr.getOrCreateTopic(topic_name)
    if pub.isSubscribed(listener, topicName=topic.name):
        pub.unsubscribe(listener, topic.name)


def set_fan_speed(on_level):
    """Map a value to a fan speed."""
    if on_level in FanSpeedRange.OFF.value:
        return FanSpeed.OFF
    if on_level in FanSpeedRange.LOW.value:
        return FanSpeed.LOW
    if on_level in FanSpeedRange.MEDIUM.value:
        return FanSpeed.MEDIUM
    return FanSpeed.HIGH
