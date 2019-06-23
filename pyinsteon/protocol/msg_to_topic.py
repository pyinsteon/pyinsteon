"""Convert a message to a topic and an args, kwargs arguments."""
import logging
from ..topics import (ALL_LINK_CLEANUP_FAILURE_REPORT,
                      ALL_LINK_CLEANUP_STATUS_REPORT, ALL_LINK_RECORD_RESPONSE,
                      ALL_LINKING_COMPLETED, BUTTON_EVENT_REPORT,
                      CANCEL_ALL_LINKING, GET_ALL_LINK_RECORD_FOR_SENDER,
                      GET_FIRST_ALL_LINK_RECORD, GET_IM_CONFIGURATION,
                      GET_IM_INFO, GET_NEXT_ALL_LINK_RECORD, LED_OFF, LED_ON,
                      MANAGE_ALL_LINK_RECORD, RESET_IM, RF_SLEEP,
                      SEND_ALL_LINK_COMMAND, SET_ACK_MESSAGE_BYTE,
                      SET_ACK_MESSAGE_TWO_BYTES, SET_HOST_DEV_CAT,
                      SET_IM_CONFIGURATION, SET_NAK_MESSAGE_BYTE,
                      START_ALL_LINKING, USER_RESET_DETECTED, X10_RECEIVED,
                      X10_SEND)
from .commands import commands
from .messages.inbound import Inbound

MSG_CONVERTER = {}
_LOGGER = logging.getLogger(__name__)


def convert_to_topic(msg: Inbound) -> (str, {}):
    """Convert a message to a topic defintion."""
    converter = MSG_CONVERTER[msg.message_id]
    return converter(msg)


def _create_rcv_std_ext_msg(topic, address, flags, cmd1, cmd2, target, user_data):
    msg_type = flags.message_type.name.lower()
    topic = '{}.{}.{}'.format(address.id, topic, msg_type)
    kwargs = {'cmd1': cmd1,
              'cmd2': cmd2,
              'target': target,
              'user_data': user_data}
    return (topic, kwargs)


def standard_received(msg: Inbound) -> (str, {}):
    """Create a topic from a STANDARD_RECEIVED message."""
    found_topic = False
    for topic in commands.get_topics(msg.cmd1, msg.cmd2, msg.flags.is_extended):
        found_topic = True
        yield _create_rcv_std_ext_msg(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, msg.target, None)
    if not found_topic:
        topic = 'standard_received'
        yield _create_rcv_std_ext_msg(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, msg.target, None)


def extended_received(msg: Inbound) -> (str, {}):
    """Create a topic from a EXTENDED_RECEIVED message."""
    found_topic = False
    for topic in commands.get_topics(msg.cmd1, msg.cmd2, msg.flags.is_extended):
        found_topic = True
        yield _create_rcv_std_ext_msg(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, msg.target, msg.user_data)
    if not found_topic:
        topic = 'extended_received'
        yield _create_rcv_std_ext_msg(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, msg.target, msg.user_data)


def x10_received(msg: Inbound) -> (str, {}):
    """Create a topic from an X10_RECEIVED message."""
    topic = X10_RECEIVED
    kwargs = {'raw_x10': msg.raw_x10,
              'x10_flag': msg.x10_flag}
    yield (topic, kwargs)


def all_linking_completed(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINKING_COMPLETED message."""
    topic = ALL_LINKING_COMPLETED
    kwargs = {'mode': msg.mode,
              'group': msg.group,
              'target': msg.target,
              'cat': msg.cat,
              'subcat': msg.subcat,
              'firmware': msg.firmware}
    yield (topic, kwargs)


def button_event_report(msg: Inbound) -> (str, {}):
    """Create a topic from a BUTTON_EVENT_REPORT message."""
    topic = BUTTON_EVENT_REPORT
    kwargs = {'event': msg.event}
    yield (topic, kwargs)


def user_reset_detected(msg: Inbound) -> (str, {}):
    """Create a topic from a USER_RESET_DETECTED message."""
    topic = USER_RESET_DETECTED
    kwargs = {}
    yield (topic, kwargs)


def all_link_cleanup_failure_report(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINK_CLEANUP_FAILURE_REPORT message."""
    topic = ALL_LINK_CLEANUP_FAILURE_REPORT
    kwargs = {'error': msg.error,
              'group': msg.group,
              'target': msg.target}
    yield (topic, kwargs)


def all_link_record_response(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINK_RECORD_RESPONSE message."""
    topic = ALL_LINK_RECORD_RESPONSE
    kwargs = {'flags': msg.flags,
              'group': msg.group,
              'target': msg.target,
              'data1': msg.data1,
              'data2': msg.data2,
              'data3': msg.data3}
    yield (topic, kwargs)


def all_link_cleanup_status_report(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINK_CLEANUP_STATUS_REPORT message."""
    topic = '{}.{}'.format(ALL_LINK_CLEANUP_STATUS_REPORT, msg.ack.name.lower())
    kwargs = {}
    yield (topic, kwargs)


def get_im_info(msg: Inbound) -> (str, {}):
    """Create a topic from an GET_IM_INFO message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), GET_IM_INFO)
    kwargs = {'address': msg.address,
              'cat': msg.cat,
              'subcat': msg.subcat,
              'firmware': msg.firmware}
    yield (topic, kwargs)


def send_all_link_command(msg: Inbound) -> (str, {}):
    """Create a topic from an SEND_ALL_LINK_COMMAND message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), SEND_ALL_LINK_COMMAND)
    kwargs = {'group': msg.group,
              'mode': msg.mode}
    yield (topic, kwargs)

def _create_send_std_ext(topic, address, flags, cmd1, cmd2, user_data, ack):
    msg_type = flags.message_type.name.lower()
    topic = '{}.{}.{}.{}'.format(ack.name.lower(), address.id, topic, msg_type)
    kwargs = {'cmd1': cmd1,
              'cmd2': cmd2,
              'user_data': None}
    return (topic, kwargs)

def send_standard_or_extended_message(msg: Inbound) -> (str, {}):
    """Convert standard and extended messages to topic."""
    def_topic = 'send_extended' if msg.flags.is_extended else 'send_standard'
    user_data = msg.user_data if msg.flags.is_extended else None

    found_topic = False
    for topic in commands.get_topics(msg.cmd1, msg.cmd2, msg.flags.is_extended):
        found_topic = True
        yield _create_send_std_ext(
            topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, user_data, msg.ack)
    if not found_topic:
        yield _create_send_std_ext(
            def_topic, msg.address, msg.flags, msg.cmd1, msg.cmd2, user_data, msg.ack)


def x10_send(msg: Inbound) -> (str, {}):
    """Create a topic from an X10_SEND message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), X10_SEND)
    kwargs = {'raw_x10': msg.raw_x10,
              'x10_flag': msg.x10_flag}
    yield (topic, kwargs)


def start_all_linking(msg: Inbound) -> (str, {}):
    """Create a topic from an start_all_linking message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), START_ALL_LINKING)
    kwargs = {'mode': msg.mode,
              'group': msg.group}
    yield (topic, kwargs)


def cancel_all_linking(msg: Inbound) -> (str, {}):
    """Create a topic from an cancel_all_linking message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), CANCEL_ALL_LINKING)
    kwargs = {}
    yield (topic, kwargs)


def set_host_dev_cat(msg: Inbound) -> (str, {}):
    """Create a topic from an set_host_dev_cat message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), SET_HOST_DEV_CAT)
    kwargs = {'cat': msg.cat,
              'subcat': msg.subcat,
              'firmware': msg.firmware}
    yield (topic, kwargs)


def reset_im(msg: Inbound) -> (str, {}):
    """Create a topic from an reset_im message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), RESET_IM)
    kwargs = {}
    yield (topic, kwargs)


def set_ack_message_byte(msg: Inbound) -> (str, {}):
    """Create a topic from an set_ack_message_byte message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), SET_ACK_MESSAGE_BYTE)
    kwargs = {'cmd2': msg.cmd2}
    yield (topic, kwargs)


def get_first_all_link_record(msg: Inbound) -> (str, {}):
    """Create a topic from an get_first_all_link_record message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), GET_FIRST_ALL_LINK_RECORD)
    kwargs = {}
    yield (topic, kwargs)


def get_next_all_link_record(msg: Inbound) -> (str, {}):
    """Create a topic from an get_next_all_link_record message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), GET_NEXT_ALL_LINK_RECORD)
    kwargs = {}
    yield (topic, kwargs)


def set_im_configuration(msg: Inbound) -> (str, {}):
    """Create a topic from an set_im_configuration message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), SET_IM_CONFIGURATION)
    kwargs = {'flags': msg.flags}
    yield (topic, kwargs)


def get_all_link_record_for_sender(msg: Inbound) -> (str, {}):
    """Create a topic from an get_all_link_record_for_sender message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), GET_ALL_LINK_RECORD_FOR_SENDER)
    kwargs = {}
    yield (topic, kwargs)


def led_on(msg: Inbound) -> (str, {}):
    """Create a topic from an led_on message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), LED_ON)
    kwargs = {}
    yield (topic, kwargs)


def led_off(msg: Inbound) -> (str, {}):
    """Create a topic from an led_off message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), LED_OFF)
    kwargs = {}
    yield (topic, kwargs)


def manage_all_link_record(msg: Inbound) -> (str, {}):
    """Create a topic from an manage_all_link_record message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), MANAGE_ALL_LINK_RECORD)
    kwargs = {'action': msg.action,
              'flags': msg.flags,
              'group': msg.group,
              'target': msg.target,
              'data1': msg.data1,
              'data2': msg.data2,
              'data3': msg.data3}
    yield (topic, kwargs)


def set_nak_message_byte(msg: Inbound) -> (str, {}):
    """Create a topic from an set_nak_message_byte message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), SET_NAK_MESSAGE_BYTE)
    kwargs = {'cmd2': msg.cmd2}
    yield (topic, kwargs)


def set_ack_message_two_bytes(msg: Inbound) -> (str, {}):
    """Create a topic from an set_ack_message_two_bytes message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), SET_ACK_MESSAGE_TWO_BYTES)
    kwargs = {'cmd1': msg.cmd1,
              'cmd2': msg.cmd2}
    yield (topic, kwargs)


def rf_sleep(msg: Inbound) -> (str, {}):
    """Create a topic from an rf_sleep message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), RF_SLEEP)
    kwargs = {}
    yield (topic, kwargs)


def get_im_configuration(msg: Inbound) -> (str, {}):
    """Create a topic from an get_im_configuration message."""
    topic = '{}.{}'.format(msg.ack.name.lower(), GET_IM_CONFIGURATION)
    kwargs = {'flags': msg.flags}
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
MSG_CONVERTER[0x60] = get_im_info
MSG_CONVERTER[0x61] = send_all_link_command
MSG_CONVERTER[0x62] = send_standard_or_extended_message
MSG_CONVERTER[0x63] = x10_send
MSG_CONVERTER[0x64] = start_all_linking
MSG_CONVERTER[0x65] = cancel_all_linking
MSG_CONVERTER[0x66] = set_host_dev_cat
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
