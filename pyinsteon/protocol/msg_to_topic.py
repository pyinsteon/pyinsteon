"""Convert a message to a topic and an args, kwargs arguments."""
import logging
from typing import Any, Dict, Tuple

from ..commands import commands
from ..constants import MessageFlagType
from ..topics import (
    ALL_LINK_CLEANUP_FAILURE_REPORT,
    ALL_LINK_CLEANUP_STATUS_REPORT,
    ALL_LINK_RECORD_RESPONSE,
    ALL_LINKING_COMPLETED,
    BUTTON_EVENT_REPORT,
    CANCEL_ALL_LINKING,
    GET_ALL_LINK_RECORD_FOR_SENDER,
    GET_FIRST_ALL_LINK_RECORD,
    GET_IM_CONFIGURATION,
    GET_IM_INFO,
    GET_NEXT_ALL_LINK_RECORD,
    LED_OFF,
    LED_ON,
    MANAGE_ALL_LINK_RECORD,
    READ_EEPROM,
    READ_EEPROM_RESPONSE,
    RESET_IM,
    RF_SLEEP,
    SEND_ALL_LINK_COMMAND,
    SET_ACK_MESSAGE_BYTE,
    SET_ACK_MESSAGE_TWO_BYTES,
    SET_HOST_DEVICE_CATEGORY,
    SET_IM_CONFIGURATION,
    SET_NAK_MESSAGE_BYTE,
    START_ALL_LINKING,
    STATUS_REQUEST,
    USER_RESET_DETECTED,
    WRITE_EEPROM,
    X10_RECEIVED,
    X10_SEND,
)
from ..utils import build_topic
from .messages.inbound import Inbound

MSG_CONVERTER = {}
_LOGGER = logging.getLogger(__name__)


def convert_to_topic(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Convert a message to a topic defintion."""
    converter = MSG_CONVERTER[msg.message_id]
    return converter(msg)


def _get_group_from_msg(topic, message_type, target, cmd2, user_data):
    """Derive the group number of the message from the message type.

    message_flag_type: MessageFlagType 0 to 7:
        DIRECT = 0: Group number is 1 unless extended then group number in d1
        DIRECT_ACK = 1: Group not applicable
        ALL_LINK_CLEANUP = 2: Group number is cmd2
        ALL_LINK_CLEANUP_ACK = 3: Not applicable
        BROADCAST = 4: Group number is in the lower byte of the target field
        DIRECT_NAK = 5: Not applicable
        ALL_LINK_BROADCAST = 6: Not applicable
        ALL_LINK_CLEANUP_NAK = 7: Not applicable
    """
    if topic == STATUS_REQUEST and message_type == MessageFlagType.DIRECT:
        return cmd2

    if message_type == MessageFlagType.DIRECT:
        if user_data:
            return user_data["d1"]
        return 1
    if message_type == MessageFlagType.ALL_LINK_CLEANUP:
        return cmd2
    if message_type in [MessageFlagType.BROADCAST, MessageFlagType.ALL_LINK_BROADCAST]:
        if not target:
            return None
        return target.low
    return None


def _create_rcv_std_ext_msg(topic, address, flags, cmd1, cmd2, target, user_data):
    if commands.use_group(topic):
        group = _get_group_from_msg(topic, flags.message_type, target, cmd2, user_data)
    else:
        group = None
    topic = build_topic(
        topic=topic,
        prefix=None,
        address=address,
        group=group,
        message_type=flags.message_type,
    )
    hops_left = flags.hops_left
    kwargs = {
        "cmd1": cmd1,
        "cmd2": cmd2,
        "target": target,
        "user_data": user_data,
        "hops_left": hops_left,
    }
    return (topic, kwargs)


def standard_received(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from a STANDARD_RECEIVED message."""
    for topic in commands.get_topics(msg.cmd1, msg.cmd2, None):
        yield _create_rcv_std_ext_msg(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, msg.target, None
        )


def extended_received(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from a EXTENDED_RECEIVED message."""
    for topic in commands.get_topics(msg.cmd1, msg.cmd2, msg.user_data):
        yield _create_rcv_std_ext_msg(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, msg.target, msg.user_data
        )


def x10_received(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an X10_RECEIVED message."""
    topic = X10_RECEIVED
    kwargs = {"raw_x10": msg.raw_x10, "x10_flag": msg.x10_flag}
    yield (topic, kwargs)


def all_linking_completed(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an ALL_LINKING_COMPLETED message."""
    topic = ALL_LINKING_COMPLETED
    kwargs = {
        "link_mode": msg.link_mode,
        "group": msg.group,
        "target": msg.target,
        "cat": msg.cat,
        "subcat": msg.subcat,
        "firmware": msg.firmware,
    }
    yield (topic, kwargs)


def button_event_report(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from a BUTTON_EVENT_REPORT message."""
    topic = BUTTON_EVENT_REPORT
    kwargs = {"event": msg.event}
    yield (topic, kwargs)


def user_reset_detected(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from a USER_RESET_DETECTED message."""
    topic = USER_RESET_DETECTED
    kwargs = {}
    yield (topic, kwargs)


def all_link_cleanup_failure_report(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an ALL_LINK_CLEANUP_FAILURE_REPORT message."""
    topic = ALL_LINK_CLEANUP_FAILURE_REPORT
    kwargs = {"error": msg.error, "group": msg.group, "target": msg.target}
    yield (topic, kwargs)


def all_link_record_response(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an ALL_LINK_RECORD_RESPONSE message."""
    topic = ALL_LINK_RECORD_RESPONSE
    kwargs = {
        "flags": msg.flags,
        "group": msg.group,
        "target": msg.target,
        "data1": msg.data1,
        "data2": msg.data2,
        "data3": msg.data3,
    }
    yield (topic, kwargs)


def all_link_cleanup_status_report(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an ALL_LINK_CLEANUP_STATUS_REPORT message."""
    topic = build_topic(ALL_LINK_CLEANUP_STATUS_REPORT, prefix=msg.ack)
    kwargs = {}
    yield (topic, kwargs)


def read_eeprom_response(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an read_eeprom message."""
    topic = build_topic(topic=READ_EEPROM_RESPONSE)
    mem_addr = (msg.mem_hi << 8) + msg.mem_low + 7

    kwargs = {
        "mem_addr": mem_addr,
        "flags": msg.flags,
        "group": msg.group,
        "target": msg.target,
        "data1": msg.data1,
        "data2": msg.data2,
        "data3": msg.data3,
    }
    yield (topic, kwargs)


def get_im_info(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an GET_IM_INFO message."""
    topic = build_topic(prefix=msg.ack, topic=GET_IM_INFO)
    kwargs = {
        "address": msg.address,
        "cat": msg.cat,
        "subcat": msg.subcat,
        "firmware": msg.firmware,
    }
    yield (topic, kwargs)


def send_all_link_command(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an SEND_ALL_LINK_COMMAND message."""
    topic = build_topic(prefix=msg.ack, topic=SEND_ALL_LINK_COMMAND)
    kwargs = {"group": msg.group, "cmd1": msg.cmd1, "cmd2": msg.cmd2}
    yield (topic, kwargs)


def _create_send_std_ext(topic, address, flags, cmd1, cmd2, user_data, ack):
    if commands.use_group(topic):
        group = _get_group_from_msg(topic, flags.message_type, None, cmd2, user_data)
    else:
        group = None

    topic = build_topic(
        topic=topic,
        prefix=str(ack),
        address=address,
        group=group,
        message_type=flags.message_type,
    )
    kwargs = {"cmd1": cmd1, "cmd2": cmd2, "user_data": user_data}
    return (topic, kwargs)


def send_standard_or_extended_message(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Convert standard and extended messages to topic."""
    def_topic = "send_extended" if msg.flags.is_extended else "send_standard"
    user_data = msg.user_data if msg.flags.is_extended else None

    found_topic = False
    user_data = None if not hasattr(msg, "user_data") else msg.user_data
    for topic in commands.get_topics(msg.cmd1, msg.cmd2, user_data):
        found_topic = True
        yield _create_send_std_ext(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, user_data, msg.ack
        )
    if not found_topic:
        yield _create_send_std_ext(
            def_topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, user_data, msg.ack
        )


def x10_send(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an X10_SEND message."""
    topic = build_topic(prefix=msg.ack, topic=X10_SEND)
    kwargs = {"raw_x10": msg.raw_x10, "x10_flag": msg.x10_flag}
    yield (topic, kwargs)


def start_all_linking(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an start_all_linking message."""
    topic = build_topic(prefix=msg.ack, topic=START_ALL_LINKING)
    kwargs = {"link_mode": msg.link_mode, "group": msg.group}
    yield (topic, kwargs)


def cancel_all_linking(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an cancel_all_linking message."""
    topic = build_topic(prefix=msg.ack, topic=CANCEL_ALL_LINKING)
    kwargs = {}
    yield (topic, kwargs)


def set_host_device_category(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an set_host_device_category message."""
    topic = build_topic(prefix=msg.ack, topic=SET_HOST_DEVICE_CATEGORY)
    kwargs = {"cat": msg.cat, "subcat": msg.subcat, "firmware": msg.firmware}
    yield (topic, kwargs)


def reset_im(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an reset_im message."""
    topic = build_topic(prefix=msg.ack, topic=RESET_IM)
    kwargs = {}
    yield (topic, kwargs)


def set_ack_message_byte(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an set_ack_message_byte message."""
    topic = build_topic(prefix=msg.ack, topic=SET_ACK_MESSAGE_BYTE)
    kwargs = {"cmd2": msg.cmd2}
    yield (topic, kwargs)


def get_first_all_link_record(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an get_first_all_link_record message."""
    topic = build_topic(prefix=msg.ack, topic=GET_FIRST_ALL_LINK_RECORD)
    kwargs = {}
    yield (topic, kwargs)


def get_next_all_link_record(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an get_next_all_link_record message."""
    topic = build_topic(prefix=msg.ack, topic=GET_NEXT_ALL_LINK_RECORD)
    kwargs = {}
    yield (topic, kwargs)


def set_im_configuration(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an set_im_configuration message."""
    topic = build_topic(prefix=msg.ack, topic=SET_IM_CONFIGURATION)

    kwargs = {
        "disable_auto_linking": msg.flags.is_auto_link,
        "monitor_mode": msg.flags.is_monitor_mode,
        "auto_led": msg.flags.is_auto_led,
        "deadman": msg.flags.is_disable_deadman,
    }
    yield (topic, kwargs)


def get_all_link_record_for_sender(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an get_all_link_record_for_sender message."""
    topic = build_topic(prefix=msg.ack, topic=GET_ALL_LINK_RECORD_FOR_SENDER)
    kwargs = {}
    yield (topic, kwargs)


def led_on(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an led_on message."""
    topic = build_topic(prefix=msg.ack, topic=LED_ON)
    kwargs = {}
    yield (topic, kwargs)


def led_off(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an led_off message."""
    topic = build_topic(prefix=msg.ack, topic=LED_OFF)
    kwargs = {}
    yield (topic, kwargs)


def manage_all_link_record(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an manage_all_link_record message."""
    topic = build_topic(prefix=msg.ack, topic=MANAGE_ALL_LINK_RECORD)
    kwargs = {
        "action": msg.action,
        "flags": msg.flags,
        "group": msg.group,
        "target": msg.target,
        "data1": msg.data1,
        "data2": msg.data2,
        "data3": msg.data3,
    }
    yield (topic, kwargs)


def set_nak_message_byte(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an set_nak_message_byte message."""
    topic = build_topic(prefix=msg.ack, topic=SET_NAK_MESSAGE_BYTE)
    kwargs = {"cmd2": msg.cmd2}
    yield (topic, kwargs)


def set_ack_message_two_bytes(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an set_ack_message_two_bytes message."""
    topic = build_topic(prefix=msg.ack, topic=SET_ACK_MESSAGE_TWO_BYTES)
    kwargs = {"cmd1": msg.cmd1, "cmd2": msg.cmd2}
    yield (topic, kwargs)


def rf_sleep(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an rf_sleep message."""
    topic = build_topic(prefix=msg.ack, topic=RF_SLEEP)
    kwargs = {}
    yield (topic, kwargs)


def get_im_configuration(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an get_im_configuration message."""
    topic = build_topic(prefix=msg.ack, topic=GET_IM_CONFIGURATION)
    kwargs = {
        "disable_auto_linking": msg.flags.is_auto_link,
        "monitor_mode": msg.flags.is_monitor_mode,
        "auto_led": msg.flags.is_auto_led,
        "deadman": msg.flags.is_disable_deadman,
    }
    yield (topic, kwargs)


def read_eeprom(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from an read_eeprom message."""
    topic = build_topic(prefix=msg.ack, topic=READ_EEPROM)
    kwargs = {"mem_hi": msg.mem_hi, "mem_low": msg.mem_low}
    yield (topic, kwargs)


def write_eeprom(msg: Inbound) -> Tuple[str, Dict[str, Any]]:
    """Create a topic from a write eeprom message."""
    topic = build_topic(prefix=msg.ack, topic=WRITE_EEPROM)
    mem_addr = (msg.mem_hi << 8) + msg.mem_low + 7
    kwargs = {
        "mem_addr": mem_addr,
        "flags": msg.flags,
        "group": msg.group,
        "target": msg.target,
        "data1": msg.data1,
        "data2": msg.data2,
        "data3": msg.data3,
    }
    yield (topic, kwargs)


MSG_CONVERTER[0x50] = standard_received
MSG_CONVERTER[0x51] = extended_received
MSG_CONVERTER[0x52] = x10_received
MSG_CONVERTER[0x53] = all_linking_completed
MSG_CONVERTER[0x54] = button_event_report
MSG_CONVERTER[0x55] = user_reset_detected
MSG_CONVERTER[0x56] = all_link_cleanup_failure_report
MSG_CONVERTER[0x57] = all_link_record_response
MSG_CONVERTER[0x58] = all_link_cleanup_status_report
MSG_CONVERTER[0x59] = read_eeprom_response
MSG_CONVERTER[0x60] = get_im_info
MSG_CONVERTER[0x61] = send_all_link_command
MSG_CONVERTER[0x62] = send_standard_or_extended_message
MSG_CONVERTER[0x63] = x10_send
MSG_CONVERTER[0x64] = start_all_linking
MSG_CONVERTER[0x65] = cancel_all_linking
MSG_CONVERTER[0x66] = set_host_device_category
MSG_CONVERTER[0x67] = reset_im
MSG_CONVERTER[0x68] = set_ack_message_byte
MSG_CONVERTER[0x69] = get_first_all_link_record
MSG_CONVERTER[0x6A] = get_next_all_link_record
MSG_CONVERTER[0x6B] = set_im_configuration
MSG_CONVERTER[0x6C] = get_all_link_record_for_sender
MSG_CONVERTER[0x6D] = led_on
MSG_CONVERTER[0x6E] = led_off
MSG_CONVERTER[0x6F] = manage_all_link_record
MSG_CONVERTER[0x70] = set_nak_message_byte
MSG_CONVERTER[0x71] = set_ack_message_two_bytes
MSG_CONVERTER[0x72] = rf_sleep
MSG_CONVERTER[0x73] = get_im_configuration
MSG_CONVERTER[0x75] = read_eeprom
MSG_CONVERTER[0x76] = write_eeprom
