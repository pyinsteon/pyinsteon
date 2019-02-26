"""Create outbound messages."""
from ..messages import MessageBase
from ..messages.message_definitions import INBOUND_MSG_DEF
from ..messages.message_flags import MessageFlags
from ..messages.message_definition import MessageDefinition
from ..messages.message_definitions import FLD_EXT_SEND_ACK
from ..constants import (MessageId, DeviceCategory, ImButtonEvents,
                         AllLinkMode, ManageAllLinkRecordAction, AckNak)
from ..address import Address
from ..messages.all_link_record_flags import AllLinkRecordFlags
from ..messages.im_config_flags import IMConfigurationFlags
from ..messages.user_data import UserData
from ..utils import set_bit, test_values_eq
from .cmd_topics import CMD_TOPICS
from ..messages.inbound import Inbound

MSG_CONVERTER = {}


def convert_to_topic(msg: Inbound) -> (str, {}):
    """Convert a message to a topic defintion."""
    converter = MSG_CONVERTER[msg.message_id]
    return converter(msg)


def standard_received(msg: Inbound) -> (str, {}):
    """Create a topic from a STANDARD_RECEIVED message."""
    cmd_topic = CMD_TOPICS[msg.cmd1]
    if not cmd_topic:
        raise ValueError('Unknown command received: cmd1: {}'.format(msg.cmd1))
    msg_type = msg.flags.message_type.name.lower()
    topic = '{}.{}.{}'.format(msg.address.id, cmd_topic, msg_type)
    kwargs = {'cmd2': msg.cmd2,
              'target': msg.target,
              'user_data': None}
    return (topic, kwargs)


def extended_received(msg: Inbound) -> (str, {}):
    """Create a topic from a EXTENDED_RECEIVED message."""
    cmd_topic = CMD_TOPICS[msg.cmd1]
    if not cmd_topic:
        raise ValueError('Unknown command received: cmd1: {}'.format(msg.cmd1))
    msg_type = msg.flags.message_type.name.lower()
    topic = '{}.{}.{}'.format(msg.address.id, cmd_topic, msg_type)
    kwargs = {'cmd2': msg.cmd2,
              'target': msg.target,
              'user_data': msg.user_data}
    return (topic, kwargs)


def x10_received(msg: Inbound) -> (str, {}):
    """Create a topic from an X10_RECEIVED message."""
    topic = 'x10_received'
    kwargs = {'raw_x10': msg.raw_x10,
              'x10_flag': msg.x10_flag}
    return (topic, kwargs)


def all_linking_completed(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINKING_COMPLETED message."""
    topic = 'all_linking_complete'
    kwargs = {'mode': msg.mode,
              'group': msg.group,
              'address': msg.address,
              'cat': msg.cat,
              'subcat': msg.subcat,
              'firmware': msg.firmware}
    return (topic, kwargs)


def button_event_report(msg: Inbound) -> (str, {}):
    """Create a topic from a BUTTON_EVENT_REPORT message."""
    topic = 'button_event_report'
    kwargs = {'event': msg.event}
    return (topic, kwargs)


def user_reset_detected(msg: Inbound) -> (str, {}):
    """Create a topic from a USER_RESET_DETECTED message."""
    topic = 'user_reset_detected'
    kwargs = {}
    return (topic, kwargs)


def all_link_cleanup_failure_report(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINK_CLEANUP_FAILURE_REPORT message."""
    topic = 'all_link_cleanup_failure_report'
    kwargs = {'error': msg.error,
              'group': msg.group,
              'address': msg.address}
    return (topic, kwargs)


def all_link_record_response(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINK_RECORD_RESPONSE message."""
    topic = 'all_link_record_response'
    kwargs = {'flags': msg.flags,
              'group': msg.group,
              'address': msg.address,
              'data1': msg.data1,
              'data2': msg.data2,
              'data3': msg.data3}
    return (topic, kwargs)


def all_link_cleanup_status_report(msg: Inbound) -> (str, {}):
    """Create a topic from an ALL_LINK_CLEANUP_STATUS_REPORT message."""
    topic = '{}.all_link_cleanup_status_report'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def get_im_info(msg: Inbound) -> (str, {}):
    """Create a topic from an GET_IM_INFO message."""
    topic = '{}.get_im_info'.format(msg.ack.name.lower())
    kwargs = {'address': msg.address,
              'cat': msg.cat,
              'subcat': msg.subcat,
              'firmware': msg.firmware}
    return (topic, kwargs)


def send_all_link_command(msg: Inbound) -> (str, {}):
    """Create a topic from an SEND_ALL_LINK_COMMAND message."""
    topic = '{}.send_all_link_command'.format(msg.ack.name.lower())
    kwargs = {'group': msg.group,
              'mode': msg.mode}
    return (topic, kwargs)


def send_standard_or_extended_message(msg: Inbound) -> (str, {}):
    """Convert standard and extended messages to topic."""
    if msg.flags.is_extended:
        return send_extended(msg)
    return send_standard(msg)


def send_standard(msg: Inbound) -> (str, {}):
    """Create a topic from an SEND_STANDARD message."""
    cmd_topic = CMD_TOPICS[msg.cmd1]
    if not cmd_topic:
        raise ValueError('Unknown command received: cmd1: {}'.format(msg.cmd1))
    msg_type = msg.flags.message_type.name.lower()
    topic = '{}.{}.{}.{}'.format(msg.ack.name.lower(), msg.address.id,
                                 cmd_topic, msg_type)
    kwargs = {'cmd2': msg.cmd2,
              'user_data': None}
    return (topic, kwargs)


def send_extended(msg: Inbound) -> (str, {}):
    """Create a topic from an SEND_STANDARD message."""
    cmd_topic = CMD_TOPICS[msg.cmd1]
    if not cmd_topic:
        raise ValueError('Unknown command received: cmd1: {}'.format(msg.cmd1))
    msg_type = msg.flags.message_type.name.lower()
    topic = '{}.{}.{}.{}'.format(str(msg.ack), msg.address.id,
                                 cmd_topic, msg_type)
    kwargs = {'cmd2': msg.cmd2,
              'user_data': msg.user_data}
    return (topic, kwargs)


def x10_send(msg: Inbound) -> (str, {}):
    """Create a topic from an x10_send message."""
    topic = '{}.x10_send'.format(msg.ack.name.lower())
    kwargs = {'raw_x10': msg.raw_x10,
              'x10_flag': msg.x10_flag}
    return (topic, kwargs)


def start_all_linking(msg: Inbound) -> (str, {}):
    """Create a topic from an start_all_linking message."""
    topic = '{}.start_all_linking'.format(msg.ack.name.lower())
    kwargs = {'mode': msg.mode,
              'group': msg.group}
    return (topic, kwargs)


def cancel_all_linking(msg: Inbound) -> (str, {}):
    """Create a topic from an cancel_all_linking message."""
    topic = '{}.cancel_all_linking'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def set_host_dev_cat(msg: Inbound) -> (str, {}):
    """Create a topic from an set_host_dev_cat message."""
    topic = '{}.set_host_dev_cat'.format(msg.ack.name.lower())
    kwargs = {'cat': msg.cat,
              'subcat': msg.subcat,
              'firmware': msg.firmware}
    return (topic, kwargs)


def reset_im(msg: Inbound) -> (str, {}):
    """Create a topic from an reset_im message."""
    topic = '{}.reset_im'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def set_ack_message_byte(msg: Inbound) -> (str, {}):
    """Create a topic from an set_ack_message_byte message."""
    topic = '{}.set_ack_message_byte'.format(msg.ack.name.lower())
    kwargs = {'cmd2': msg.cmd2}
    return (topic, kwargs)


def get_first_all_link_record(msg: Inbound) -> (str, {}):
    """Create a topic from an get_first_all_link_record message."""
    topic = '{}.get_first_all_link_record'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def get_next_all_link_record(msg: Inbound) -> (str, {}):
    """Create a topic from an get_next_all_link_record message."""
    topic = '{}.get_next_all_link_record'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def set_im_configuration(msg: Inbound) -> (str, {}):
    """Create a topic from an set_im_configuration message."""
    topic = '{}.set_im_configuration'.format(msg.ack.name.lower())
    kwargs = {'flags': msg.flags}
    return (topic, kwargs)


def get_all_link_record_for_sender(msg: Inbound) -> (str, {}):
    """Create a topic from an get_all_link_record_for_sender message."""
    topic = '{}.get_all_link_record_for_sender'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def led_on(msg: Inbound) -> (str, {}):
    """Create a topic from an led_on message."""
    topic = '{}.led_on'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def led_off(msg: Inbound) -> (str, {}):
    """Create a topic from an led_off message."""
    topic = '{}.led_off'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def manage_all_link_record(msg: Inbound) -> (str, {}):
    """Create a topic from an manage_all_link_record message."""
    topic = '{}.manage_all_link_record'.format(msg.ack.name.lower())
    kwargs = {'action': msg.action,
              'flags': msg.flags,
              'group': msg.group,
              'address': msg.address,
              'data1': msg.data1,
              'data2': msg.data2,
              'data3': msg.data3}
    return (topic, kwargs)


def set_nak_message_byte(msg: Inbound) -> (str, {}):
    """Create a topic from an set_nak_message_byte message."""
    topic = '{}.set_nak_message_byte'.format(msg.ack.name.lower())
    kwargs = {'cmd2': msg.cmd2}
    return (topic, kwargs)


def set_ack_message_two_bytes(msg: Inbound) -> (str, {}):
    """Create a topic from an set_ack_message_two_bytes message."""
    topic = '{}.set_ack_message_two_bytes'.format(msg.ack.name.lower())
    kwargs = {'cmd1': msg.cmd1,
              'cmd2': msg.cmd2}
    return (topic, kwargs)


def rf_sleep(msg: Inbound) -> (str, {}):
    """Create a topic from an rf_sleep message."""
    topic = '{}.rf_sleep'.format(msg.ack.name.lower())
    kwargs = {}
    return (topic, kwargs)


def get_im_configuration(msg: Inbound) -> (str, {}):
    """Create a topic from an get_im_configuration message."""
    topic = '{}.get_im_configuration'.format(msg.ack.name.lower())
    kwargs = {'flags': msg.flags}
    return (topic, kwargs)


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
