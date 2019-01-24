"""Create outbound messages."""
from . import MessageBase
from .message_definitions import OUTBOUND_MSG_DEF
from .message_flags import MessageFlags
from .message_definition import MessageDefinition
from .message_definitions import FLD_EXT_SEND
from ..constants import (MessageId, DeviceCategory, ImButtonEvents, 
                         AllLinkMode, ManageAlLinkRecordAction)
from ..address import Address
from .all_link_record_flags import AllLinkRecordFlags
from .im_config_flags import IMConfigurationFlags
from .user_data import UserData
from ..utils import set_bit


class Outbound(MessageBase):
    """Outbound message class."""


def get_im_info():
    """Create a GET_IM_INFO outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.GET_IM_INFO]
    return Outbound(msg_def, **kwargs)


def send_all_link_command(group: int, mode: AllLinkMode):
    """Create a SEND_ALL_LINK_COMMAND outbound message."""
    kwargs = {'group': group,
              'mode': mode}

    msg_def = OUTBOUND_MSG_DEF[MessageId.SEND_ALL_LINK_COMMAND]
    return Outbound(msg_def, **kwargs)


def send_standard(address: Address, flags: MessageFlags, cmd1: int, cmd2: int):
    """Create a SEND_STANDARD outbound message."""
    msg_flags = set_bit(bytes(MessageFlags(flags)), 4, False)
    kwargs = {'address': address,
              'flags': msg_flags,
              'cmd1': cmd1,
              'cmd2': cmd2}
    msg_def = OUTBOUND_MSG_DEF[MessageId.SEND_STANDARD]
    return Outbound(msg_def, **kwargs)


def send_extended(address: Address, flags: MessageFlags, cmd1: int, cmd2: int,
                  user_data: UserData):
    """Create a SEND_EXTENDED outbound message."""
    msg_flags = set_bit(bytes(MessageFlags(flags)), 4, True)
    kwargs = {'address': address,
              'flags': msg_flags,
              'cmd1': cmd1,
              'cmd2': cmd2,
              'user_data': user_data}
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND)
    return Outbound(msg_def, **kwargs)


def x10_send(raw_x10: int, x10_flag: int):
    """Create a X10_SEND outbound message."""
    kwargs = {'raw_x10': raw_x10,
              'x10_flag': x10_flag}
    msg_def = OUTBOUND_MSG_DEF[MessageId.X10_SEND]
    return Outbound(msg_def, **kwargs)


def start_all_linking(mode: AllLinkMode, group: int):
    """Create a START_ALL_LINKING outbound message."""
    kwargs = {'mode': mode,
              'group': group}
    msg_def = OUTBOUND_MSG_DEF[MessageId.START_ALL_LINKING]
    return Outbound(msg_def, **kwargs)


def cancel_all_linking():
    """Create a CANCEL_ALL_LINKING outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.CANCEL_ALL_LINKING]
    return Outbound(msg_def, **kwargs)


def set_host_dev_cat(cat: DeviceCategory, subcat: int, firmware: int):
    """Create a SET_HOST_DEV_CAT outbound message."""
    kwargs = {'cat': cat,
              'subcat': subcat,
              'firmware': firmware}
    msg_def = OUTBOUND_MSG_DEF[MessageId.SET_HOST_DEV_CAT]
    return Outbound(msg_def, **kwargs)


def reset_im():
    """Create a RESET_IM outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.RESET_IM]
    return Outbound(msg_def, **kwargs)


def set_ack_message_byte(cmd2: int):
    """Create a SET_ACK_MESSAGE_BYTE outbound message."""
    kwargs = {'cmd2': cmd2}
    msg_def = OUTBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_BYTE]
    return Outbound(msg_def, **kwargs)


def get_first_all_link_record():
    """Create a GET_FIRST_ALL_LINK_RECORD outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.GET_FIRST_ALL_LINK_RECORD]
    return Outbound(msg_def, **kwargs)


def get_next_all_link_record():
    """Create a GET_NEXT_ALL_LINK_RECORD outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.GET_NEXT_ALL_LINK_RECORD]
    return Outbound(msg_def, **kwargs)


def set_im_configuration(flags: IMConfigurationFlags):
    """Create a SET_IM_CONFIGURATION outbound message."""
    kwargs = {'flags': flags}
    msg_def = OUTBOUND_MSG_DEF[MessageId.SET_IM_CONFIGURATION]
    return Outbound(msg_def, **kwargs)


def get_all_link_record_for_sender():
    """Create a GET_ALL_LINK_RECORD_FOR_SENDER outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.GET_ALL_LINK_RECORD_FOR_SENDER]
    return Outbound(msg_def, **kwargs)


def led_on():
    """Create a LED_ON outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.LED_ON]
    return Outbound(msg_def, **kwargs)


def led_off():
    """Create a LED_OFF outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.LED_OFF]
    return Outbound(msg_def, **kwargs)


def manage_all_link_record(action: ManageAlLinkRecordAction,
                           flags: AllLinkRecordFlags, group: int,
                           address: Address, data1: int, data2: int,
                           data3: int):
    """Create a MANAGE_ALL_LINK_RECORD outbound message."""
    kwargs = {'action': action,
              'flags': flags,
              'group': group,
              'address': address,
              'data1': data1,
              'data2': data2,
              'data3': data3}
    msg_def = OUTBOUND_MSG_DEF[MessageId.MANAGE_ALL_LINK_RECORD]
    return Outbound(msg_def, **kwargs)


def set_nak_message_byte(cmd2: int):
    """Create a SET_NAK_MESSAGE_BYTE outbound message."""
    kwargs = {'cmd2': cmd2}
    msg_def = OUTBOUND_MSG_DEF[MessageId.SET_NAK_MESSAGE_BYTE]
    return Outbound(msg_def, **kwargs)


def set_ack_message_two_bytes(cmd1: int, cmd2: int):
    """Create a SET_ACK_MESSAGE_TWO_BYTES outbound message."""
    kwargs = {'cmd1': cmd1,
              'cmd2': cmd2}
    msg_def = OUTBOUND_MSG_DEF[MessageId.SET_ACK_MESSAGE_TWO_BYTES]
    return Outbound(msg_def, **kwargs)


def rf_sleep():
    """Create a RF_SLEEP outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.RF_SLEEP]
    return Outbound(msg_def, **kwargs)


def get_im_configuration():
    """Create a GET_IM_CONFIGURATION outbound message."""
    kwargs = {}
    msg_def = OUTBOUND_MSG_DEF[MessageId.GET_IM_CONFIGURATION]
    return Outbound(msg_def, **kwargs)
