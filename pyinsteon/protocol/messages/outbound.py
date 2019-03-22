"""Create outbound messages."""
import inspect

from . import MessageBase
from .. import topic_to_message_handler
from ...address import Address
from ...constants import (AllLinkMode, DeviceCategory,
                          ManageAllLinkRecordAction, MessageId)
from ...topics import (CANCEL_ALL_LINKING, GET_ALL_LINK_RECORD_FOR_SENDER,
                       GET_FIRST_ALL_LINK_RECORD, GET_IM_CONFIGURATION,
                       GET_IM_INFO, GET_NEXT_ALL_LINK_RECORD, LED_OFF, LED_ON,
                       MANAGE_ALL_LINK_RECORD, RESET_IM, RF_SLEEP,
                       SEND_ALL_LINK_COMMAND, SEND_EXTENDED, SEND_STANDARD,
                       SET_ACK_MESSAGE_BYTE, SET_ACK_MESSAGE_TWO_BYTES,
                       SET_HOST_DEV_CAT, SET_IM_CONFIGURATION,
                       SET_NAK_MESSAGE_BYTE, START_ALL_LINKING, X10_SEND)
from .all_link_record_flags import AllLinkRecordFlags
from .im_config_flags import IMConfigurationFlags
from .message_definition import MessageDefinition
from .message_definitions import FLD_EXT_SEND, OUTBOUND_MSG_DEF
from .message_flags import MessageFlags
from .user_data import UserData


class Outbound(MessageBase):
    """Outbound message class."""


def _create_outbound_message(frame) -> Outbound:
    """Create an Outbound message."""
    args, _, _, values = inspect.getargvalues(frame)
    kwargs = {}
    for arg in args:
        kwargs[arg] = values.get(arg)
    msg_id = getattr(MessageId, kwargs['topic'].upper())
    msg_def = OUTBOUND_MSG_DEF[msg_id]
    return Outbound(msg_def, **kwargs)


@topic_to_message_handler(topic=GET_IM_INFO)
def get_im_info(topic=GET_IM_INFO) -> Outbound:
    """Create a GET_IM_INFO outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=SEND_ALL_LINK_COMMAND)
def send_all_link_command(group: int, mode: AllLinkMode, topic=SEND_ALL_LINK_COMMAND) -> Outbound:
    """Create a SEND_ALL_LINK_COMMAND outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=SEND_STANDARD)
def send_standard(address: Address, flags: MessageFlags, cmd1: int, cmd2: int, topic=SEND_STANDARD) -> Outbound:
    """Create a SEND_STANDARD outbound message."""
    return _create_outbound_message(inspect.currentframe())

@topic_to_message_handler(topic=SEND_EXTENDED)
def send_extended(address: Address, flags: MessageFlags, cmd1: int, cmd2: int,
                  user_data: UserData, topic=SEND_EXTENDED) -> Outbound:
    """Create a SEND_EXTENDED outbound message."""
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    kwargs = {}
    for arg in args:
        kwargs[arg] = values.get(arg)
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND)
    return Outbound(msg_def, **kwargs)


@topic_to_message_handler(topic=X10_SEND)
def x10_send(raw_x10: int, x10_flag: int, topic=X10_SEND) -> Outbound:
    """Create a X10_SEND outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=START_ALL_LINKING)
def start_all_linking(mode: AllLinkMode, group: int, topic=X10_SEND) -> Outbound:
    """Create a START_ALL_LINKING outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=CANCEL_ALL_LINKING)
def cancel_all_linking(topic=CANCEL_ALL_LINKING) -> Outbound:
    """Create a CANCEL_ALL_LINKING outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=SET_HOST_DEV_CAT)
def set_host_dev_cat(cat: DeviceCategory, subcat: int, firmware: int, topic=SET_HOST_DEV_CAT) -> Outbound:
    """Create a SET_HOST_DEV_CAT outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=RESET_IM)
def reset_im(topic=SET_HOST_DEV_CAT) -> Outbound:
    """Create a RESET_IM outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=SET_ACK_MESSAGE_BYTE)
def set_ack_message_byte(cmd2: int, topic=SET_HOST_DEV_CAT) -> Outbound:
    """Create a SET_ACK_MESSAGE_BYTE outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=GET_FIRST_ALL_LINK_RECORD)
def get_first_all_link_record(topic=SET_HOST_DEV_CAT) -> Outbound:
    """Create a GET_FIRST_ALL_LINK_RECORD outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=GET_NEXT_ALL_LINK_RECORD)
def get_next_all_link_record(topic=GET_NEXT_ALL_LINK_RECORD) -> Outbound:
    """Create a GET_NEXT_ALL_LINK_RECORD outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=SET_IM_CONFIGURATION)
def set_im_configuration(flags: IMConfigurationFlags, topic=SET_IM_CONFIGURATION) -> Outbound:
    """Create a SET_IM_CONFIGURATION outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=GET_ALL_LINK_RECORD_FOR_SENDER)
def get_all_link_record_for_sender(topic=GET_ALL_LINK_RECORD_FOR_SENDER) -> Outbound:
    """Create a GET_ALL_LINK_RECORD_FOR_SENDER outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=LED_ON)
def led_on(topic=LED_ON) -> Outbound:
    """Create a LED_ON outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=LED_OFF)
def led_off(topic=LED_OFF) -> Outbound:
    """Create a LED_OFF outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=MANAGE_ALL_LINK_RECORD)
def manage_all_link_record(action: ManageAllLinkRecordAction,
                           flags: AllLinkRecordFlags, group: int,
                           address: Address, data1: int, data2: int,
                           data3: int, topic=MANAGE_ALL_LINK_RECORD) -> Outbound:
    """Create a MANAGE_ALL_LINK_RECORD outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=SET_NAK_MESSAGE_BYTE)
def set_nak_message_byte(cmd2: int, topic=SET_NAK_MESSAGE_BYTE) -> Outbound:
    """Create a SET_NAK_MESSAGE_BYTE outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=SET_ACK_MESSAGE_TWO_BYTES)
def set_ack_message_two_bytes(cmd1: int, cmd2: int, topic=SET_ACK_MESSAGE_TWO_BYTES) -> Outbound:
    """Create a SET_ACK_MESSAGE_TWO_BYTES outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=RF_SLEEP)
def rf_sleep(topic=RF_SLEEP) -> Outbound:
    """Create a RF_SLEEP outbound message."""
    return _create_outbound_message(inspect.currentframe())


@topic_to_message_handler(topic=GET_IM_CONFIGURATION)
def get_im_configuration(topic=GET_IM_CONFIGURATION) -> Outbound:
    """Create a GET_IM_CONFIGURATION outbound message."""
    return _create_outbound_message(inspect.currentframe())
