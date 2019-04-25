"""Create outbound messages."""
from ... import pub
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
from .message_definitions import FLD_EXT_SEND, FLD_STD_SEND, OUTBOUND_MSG_DEF
from .message_flags import MessageFlags
from .user_data import UserData


class Outbound(MessageBase):
    """Outbound message class."""


def _create_outbound_message(**kwargs) -> Outbound:
    """Create an Outbound message."""
    topic = kwargs['topic'].name.split('.')[1]
    msg_id = getattr(MessageId, topic.upper())
    msg_def = OUTBOUND_MSG_DEF[msg_id]
    msg = Outbound(msg_def, **kwargs)
    pub.sendMessage('send_message.{}'.format(topic),
                    msg=msg)


@topic_to_message_handler(topic=GET_IM_INFO)
def get_im_info(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_IM_INFO outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=SEND_ALL_LINK_COMMAND)
def send_all_link_command(group: int, mode: AllLinkMode, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SEND_ALL_LINK_COMMAND outbound message."""
    _create_outbound_message(group=group, mode=mode, topic=topic)


@topic_to_message_handler(topic=SEND_STANDARD)
def send_standard(address: Address, flags: MessageFlags, cmd1: int, cmd2: int,
                  topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SEND_STANDARD outbound message."""
    main_topic = topic.name.split('.')[1]
    kwargs = {'address': address,
              'flags': flags,
              'cmd1': cmd1,
              'cmd2': cmd2,
              'topic': topic}
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_STD_SEND)
    pub.sendMessage('send_message.{}'.format(main_topic),
                    msg=Outbound(msg_def, **kwargs))


@topic_to_message_handler(topic=SEND_EXTENDED)
def send_extended(address: Address, flags: MessageFlags, cmd1: int, cmd2: int,
                  user_data: UserData, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SEND_EXTENDED outbound message."""
    main_topic = topic.name.split('.')[1]
    kwargs = {'address': address,
              'flags': flags,
              'cmd1': cmd1,
              'cmd2': cmd2,
              'user_data': user_data,
              'topic': topic}
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND)
    pub.sendMessage('send_message.{}'.format(main_topic),
                    msg=Outbound(msg_def, **kwargs))


@topic_to_message_handler(topic=X10_SEND)
def x10_send(raw_x10: int, x10_flag: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a X10_SEND outbound message."""
    _create_outbound_message(raw_x10=raw_x10, x10_flag=x10_flag, topic=topic)


@topic_to_message_handler(topic=START_ALL_LINKING)
def start_all_linking(mode: AllLinkMode, group: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a START_ALL_LINKING outbound message."""
    _create_outbound_message(mode=mode, group=group, topic=topic)


@topic_to_message_handler(topic=CANCEL_ALL_LINKING)
def cancel_all_linking(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a CANCEL_ALL_LINKING outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=SET_HOST_DEV_CAT)
def set_host_dev_cat(cat: DeviceCategory, subcat: int, firmware: int,
                     topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_HOST_DEV_CAT outbound message."""
    _create_outbound_message(cat=cat, subcat=subcat, firmware=firmware, topic=topic)


@topic_to_message_handler(topic=RESET_IM)
def reset_im(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a RESET_IM outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=SET_ACK_MESSAGE_BYTE)
def set_ack_message_byte(cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_ACK_MESSAGE_BYTE outbound message."""
    _create_outbound_message(cmd2=cmd2, topic=topic)


@topic_to_message_handler(topic=GET_FIRST_ALL_LINK_RECORD)
def get_first_all_link_record(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_FIRST_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=GET_NEXT_ALL_LINK_RECORD)
def get_next_all_link_record(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_NEXT_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=SET_IM_CONFIGURATION)
def set_im_configuration(flags: IMConfigurationFlags, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_IM_CONFIGURATION outbound message."""
    _create_outbound_message(flags=flags, topic=topic)


@topic_to_message_handler(topic=GET_ALL_LINK_RECORD_FOR_SENDER)
def get_all_link_record_for_sender(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_ALL_LINK_RECORD_FOR_SENDER outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=LED_ON)
def led_on(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a LED_ON outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=LED_OFF)
def led_off(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a LED_OFF outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=MANAGE_ALL_LINK_RECORD)
def manage_all_link_record(action: ManageAllLinkRecordAction,
                           flags: AllLinkRecordFlags, group: int,
                           address: Address, data1: int, data2: int,
                           data3: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a MANAGE_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(action=action, flags=flags, group=group,
                             address=address, data1=data1, data2=data2,
                             data3=data3, topic=topic)


@topic_to_message_handler(topic=SET_NAK_MESSAGE_BYTE)
def set_nak_message_byte(cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_NAK_MESSAGE_BYTE outbound message."""
    _create_outbound_message(cmd2=cmd2, topic=topic)


@topic_to_message_handler(topic=SET_ACK_MESSAGE_TWO_BYTES)
def set_ack_message_two_bytes(cmd1: int, cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_ACK_MESSAGE_TWO_BYTES outbound message."""
    _create_outbound_message(cmd1=cmd1, cmd2=cmd2, topic=topic)


@topic_to_message_handler(topic=RF_SLEEP)
def rf_sleep(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a RF_SLEEP outbound message."""
    _create_outbound_message(topic=topic)


@topic_to_message_handler(topic=GET_IM_CONFIGURATION)
def get_im_configuration(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_IM_CONFIGURATION outbound message."""
    _create_outbound_message(topic=topic)
