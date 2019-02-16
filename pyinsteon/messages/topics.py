"""Create outbound messages."""
from . import MessageBase
from .message_definitions import INBOUND_MSG_DEF
from .message_flags import MessageFlags
from .message_definition import MessageDefinition
from .message_definitions import FLD_EXT_SEND_ACK
from ..constants import (MessageId, DeviceCategory, ImButtonEvents,
                         AllLinkMode, ManageAllLinkRecordAction, AckNak)
from ..address import Address
from .all_link_record_flags import AllLinkRecordFlags
from .im_config_flags import IMConfigurationFlags
from .user_data import UserData
from ..utils import set_bit, test_values_eq


class Template(MessageBase):
    """Outbound message class."""

    def __eq__(self, other: MessageBase):
        """Test for equality."""
        if not (isinstance(other, MessageBase) and
                self.message_id == other.message_id):
            return False
        found = True
        for fld in self.fields:
            if fld.name == 'ack':
                return found
            if not hasattr(other, fld.name):
                return False
            found = test_values_eq(getattr(other, fld.name),
                                   getattr(self, fld.name))
        return found


def standard_received(address: Address = None, target: Address = None,
                      flags: MessageFlags = None, cmd1: int = None,
                      cmd2: int = None) -> Template:
    """Create a STANDARD_RECEIVED outbound message."""
    kwargs = {'address': address,
              'target': target,
              'flags': flags,
              'cmd1': cmd1,
              'cmd2': cmd2}
    msg_def = INBOUND_MSG_DEF[MessageId.STANDARD_RECEIVED]
    return Template(msg_def, **kwargs)


def extended_received(address: Address = None, target: Address = None,
                      flags: MessageFlags = None, cmd1: int = None,
                      cmd2: int = None, user_data: UserData = None) -> Template:
    """Create a EXTENDED_RECEIVED outbound message."""
    kwargs = {'address': address,
              'target': target,
              'flags': flags,
              'cmd1': cmd1,
              'cmd2': cmd2,
              'user_data': user_data}
    msg_def = INBOUND_MSG_DEF[MessageId.EXTENDED_RECEIVED]
    return Template(msg_def, **kwargs)


def x10_received(raw_x10: int = None, x10_flag: int = None) -> Template:
    """Create a X10_RECEIVED outbound message."""
    kwargs = {'raw_x10': raw_x10,
              'x10_flag': x10_flag}
    msg_def = INBOUND_MSG_DEF[MessageId.X10_RECEIVED]
    return Template(msg_def, **kwargs)


def all_linking_completed(mode: AllLinkMode = None, group: int = None,
                          address: Address = None, cat: DeviceCategory = None,
                          subcat: int = None,
                          firmware: int = None) -> Template:
    """Create a ALL_LINKING_COMPLETED outbound message."""
    kwargs = {'mode': mode,
              'group': group,
              'address': address,
              'cat': cat,
              'subcat': subcat,
              'firmware': firmware}
    msg_def = INBOUND_MSG_DEF[MessageId.ALL_LINKING_COMPLETED]
    return Template(msg_def, **kwargs)


def button_event_report(event: ImButtonEvents = None) -> Template:
    """Create a BUTTON_EVENT_REPORT outbound message."""
    kwargs = {'event': event}
    msg_def = INBOUND_MSG_DEF[MessageId.BUTTON_EVENT_REPORT]
    return Template(msg_def, **kwargs)


def user_reset_detected() -> Template:
    """Create a USER_RESET_DETECTED outbound message."""
    kwargs = {}
    msg_def = INBOUND_MSG_DEF[MessageId.USER_RESET_DETECTED]
    return Template(msg_def, **kwargs)


def all_link_cleanup_failure_report(error: int = None, group: int = None,
                                    address: Address = None) -> Template:
    """Create a ALL_LINK_CLEANUP_FAILURE_REPORT outbound message."""
    kwargs = {'error': error,
              'group': group,
              'address': address}
    msg_def = INBOUND_MSG_DEF[MessageId.ALL_LINK_CLEANUP_FAILURE_REPORT]
    return Template(msg_def, **kwargs)


def all_link_record_response(flags: AllLinkRecordFlags = None, group: int = None,
                             address: Address = None, data1: int = None,
                             data2: int = None, data3: int = None) -> Template:
    """Create a ALL_LINK_RECORD_RESPONSE outbound message."""
    kwargs = {'flags': flags,
              'group': group,
              'address': address,
              'data1': data1,
              'data2': data2,
              'data3': data3}
    msg_def = INBOUND_MSG_DEF[MessageId.ALL_LINK_RECORD_RESPONSE]
    return Template(msg_def, **kwargs)


def all_link_cleanup_status_report(ack: AckNak = None) -> Template:
    """Create a ALL_LINK_CLEANUP_STATUS_REPORT outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.ALL_LINK_CLEANUP_STATUS_REPORT]
    return Template(msg_def, **kwargs)


def get_im_info(address: Address = None, cat: DeviceCategory = None,
                subcat: int = None, firmware: int = None,
                ack: AckNak = None) -> Template:
    """Create a GET_IM_INFO outbound message."""
    kwargs = {'address': address,
              'cat': cat,
              'subcat': subcat,
              'firmware': firmware,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.GET_IM_INFO]
    return Template(msg_def, **kwargs)


def send_all_link_command(group: int = None,
                          mode: AllLinkMode = None,
                          ack: AckNak = None) -> Template:
    """Create a SEND_ALL_LINK_COMMAND outbound message."""
    kwargs = {'group': group,
              'mode': mode,
              'ack': ack}

    msg_def = INBOUND_MSG_DEF[MessageId.SEND_ALL_LINK_COMMAND]
    return Template(msg_def, **kwargs)


def send_standard(address: Address = None, flags: MessageFlags = None,
                  cmd1: int = None, cmd2: int = None,
                  ack: AckNak = None) -> Template:
    """Create a SEND_STANDARD outbound message."""
    msg_flags = set_bit(bytes(MessageFlags(flags)), 4, False)
    kwargs = {'address': address,
              'flags': msg_flags,
              'cmd1': cmd1,
              'cmd2': cmd2,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.SEND_STANDARD]
    return Template(msg_def, **kwargs)


def send_extended(address: Address = None, flags: MessageFlags = None,
                  cmd1: int = None, cmd2: int = None,
                  user_data: UserData = None, ack: AckNak = None) -> Template:
    """Create a SEND_EXTENDED outbound message."""
    msg_flags = set_bit(bytes(MessageFlags(flags)), 4, True)
    kwargs = {'address': address,
              'flags': msg_flags,
              'cmd1': cmd1,
              'cmd2': cmd2,
              'user_data': user_data,
              'ack': ack}
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND_ACK)
    return Template(msg_def, **kwargs)


def x10_send(raw_x10: int = None, x10_flag: int = None,
            ack: AckNak = None) -> Template:
    """Create a X10_SEND outbound message."""
    kwargs = {'raw_x10': raw_x10,
              'x10_flag': x10_flag,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.X10_SEND]
    return Template(msg_def, **kwargs)


def start_all_linking(mode: AllLinkMode = None, group: int = None,
                      ack: AckNak = None) -> Template:
    """Create a START_ALL_LINKING outbound message."""
    kwargs = {'mode': mode,
              'group': group,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.START_ALL_LINKING]
    return Template(msg_def, **kwargs)


def cancel_all_linking(ack: AckNak = None) -> Template:
    """Create a CANCEL_ALL_LINKING outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.CANCEL_ALL_LINKING]
    return Template(msg_def, **kwargs)


def set_host_dev_cat(cat: DeviceCategory = None, subcat: int = None,
                     firmware: int = None, ack: AckNak = None) -> Template:
    """Create a SET_HOST_DEV_CAT outbound message."""
    kwargs = {'cat': cat,
              'subcat': subcat,
              'firmware': firmware,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.SET_HOST_DEV_CAT]
    return Template(msg_def, **kwargs)


def reset_im(ack: AckNak = None) -> Template:
    """Create a RESET_IM outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.RESET_IM]
    return Template(msg_def, **kwargs)


def set_ack_message_byte(cmd2: int = None, ack: AckNak = None) -> Template:
    """Create a SET_ACK_MESSAGE_BYTE outbound message."""
    kwargs = {'cmd2': cmd2,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_BYTE]
    return Template(msg_def, **kwargs)


def get_first_all_link_record(ack: AckNak = None) -> Template:
    """Create a GET_FIRST_ALL_LINK_RECORD outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.GET_FIRST_ALL_LINK_RECORD]
    return Template(msg_def, **kwargs)


def get_next_all_link_record(ack: AckNak = None) -> Template:
    """Create a GET_NEXT_ALL_LINK_RECORD outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.GET_NEXT_ALL_LINK_RECORD]
    return Template(msg_def, **kwargs)


def set_im_configuration(flags: IMConfigurationFlags = None,
                         ack: AckNak = None) -> Template:
    """Create a SET_IM_CONFIGURATION outbound message."""
    kwargs = {'flags': flags,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.SET_IM_CONFIGURATION]
    return Template(msg_def, **kwargs)


def get_all_link_record_for_sender(ack: AckNak = None) -> Template:
    """Create a GET_ALL_LINK_RECORD_FOR_SENDER outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.GET_ALL_LINK_RECORD_FOR_SENDER]
    return Template(msg_def, **kwargs)


def led_on(ack: AckNak = None) -> Template:
    """Create a LED_ON outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.LED_ON]
    return Template(msg_def, **kwargs)


def led_off(ack: AckNak = None) -> Template:
    """Create a LED_OFF outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.LED_OFF]
    return Template(msg_def, **kwargs)


def manage_all_link_record(action: ManageAllLinkRecordAction = None,
                           flags: AllLinkRecordFlags = None, group: int = None,
                           address: Address = None, data1: int = None,
                           data2: int = None, data3: int = None,
                           ack: AckNak = None) -> Template:
    """Create a MANAGE_ALL_LINK_RECORD outbound message."""
    kwargs = {'action': action,
              'flags': flags,
              'group': group,
              'address': address,
              'data1': data1,
              'data2': data2,
              'data3': data3,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.MANAGE_ALL_LINK_RECORD]
    return Template(msg_def, **kwargs)


def set_nak_message_byte(cmd2: int = None, ack: AckNak = None) -> Template:
    """Create a SET_NAK_MESSAGE_BYTE outbound message."""
    kwargs = {'cmd2': cmd2,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.SET_NAK_MESSAGE_BYTE]
    return Template(msg_def, **kwargs)


def set_ack_message_two_bytes(cmd1: int = None, cmd2: int = None,
                  ack: AckNak = None) -> Template:
    """Create a SET_ACK_MESSAGE_TWO_BYTES outbound message."""
    kwargs = {'cmd1': cmd1,
              'cmd2': cmd2,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_TWO_BYTES]
    return Template(msg_def, **kwargs)


def rf_sleep(ack: AckNak = None) -> Template:
    """Create a RF_SLEEP outbound message."""
    kwargs = {'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.RF_SLEEP]
    return Template(msg_def, **kwargs)


def get_im_configuration(flags: IMConfigurationFlags = None,
                         ack: AckNak = None) -> Template:
    """Create a GET_IM_CONFIGURATION outbound message."""
    kwargs = {'flags': flags,
              'ack': ack}
    msg_def = INBOUND_MSG_DEF[MessageId.GET_IM_CONFIGURATION]
    return Template(msg_def, **kwargs)
