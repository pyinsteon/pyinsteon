"""Create outbound messages."""
import logging
from ... import pub
from ...address import Address
from ...constants import (
    AllLinkMode,
    DeviceCategory,
    ManageAllLinkRecordAction,
    MessageId,
    X10CommandType,
)
from ...topics import (
    ALL_LINK_CLEANUP_STATUS_REPORT,
    CANCEL_ALL_LINKING,
    GET_ALL_LINK_RECORD_FOR_SENDER,
    GET_FIRST_ALL_LINK_RECORD,
    GET_IM_CONFIGURATION,
    GET_IM_INFO,
    GET_NEXT_ALL_LINK_RECORD,
    LED_OFF,
    LED_ON,
    MANAGE_ALL_LINK_RECORD,
    RESET_IM,
    RF_SLEEP,
    SEND_ALL_LINK_COMMAND,
    SEND_EXTENDED,
    SEND_STANDARD,
    SET_ACK_MESSAGE_BYTE,
    SET_ACK_MESSAGE_TWO_BYTES,
    SET_HOST_DEV_CAT,
    SET_IM_CONFIGURATION,
    SET_NAK_MESSAGE_BYTE,
    START_ALL_LINKING,
    X10_SEND,
)
from ...utils import publish_topic, subscribe_topic
from ..topic_converters import topic_to_message_handler, topic_to_message_type
from . import MessageBase
from .all_link_record_flags import AllLinkRecordFlags
from .im_config_flags import IMConfigurationFlags
from .message_definition import MessageDefinition
from .message_definitions import FLD_EXT_SEND, FLD_STD_SEND, OUTBOUND_MSG_DEF
from .message_flags import MessageFlags
from .message_flags import create as create_flags
from .user_data import UserData

# pylint: disable=invalid-name
topic_register = {}

_LOGGER = logging.getLogger(__name__)


def register_outbound_handlers():
    """Register outbound handlers."""
    for topic in topic_register:
        func = topic_register[topic]
        subscribe_topic(func, topic)


class Outbound(MessageBase):
    """Outbound message class."""

    def __eq__(self, other):
        """Needed to allow a prioritized queue work.

        Always returns True.
        """
        return True

    def __gt__(self, other):
        """Needed to allow a prioritized queue work.

        Always returns False.
        """
        return False

    def __lt__(self, other):
        """Needed to allow a prioritized queue work.

        Always returns False.
        """
        return False

    def __hash__(self):
        """Needed to allow a prioritized queue work.

        Return hash of str(self).
        """
        return hash(str(self))


def _create_outbound_message(topic, priority=5, **kwargs) -> Outbound:
    """Create an Outbound message."""
    topic = topic.name.split(".")[1]
    msg_id = getattr(MessageId, topic.upper())
    msg_def = OUTBOUND_MSG_DEF[msg_id]
    msg = Outbound(msg_def, **kwargs)
    publish_topic("send_message.{}".format(topic), msg=msg, priority=priority)


@topic_to_message_handler(
    register_list=topic_register, topic=ALL_LINK_CLEANUP_STATUS_REPORT
)
def all_link_cleanup_status_report(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a ALL_LINK_CLEANUP_STATUS_REPORT outbound message."""
    _create_outbound_message(topic=topic, priority=1)


@topic_to_message_handler(register_list=topic_register, topic=GET_IM_INFO)
def get_im_info(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_IM_INFO outbound message."""
    _create_outbound_message(topic=topic, priority=1)


@topic_to_message_handler(register_list=topic_register, topic=SEND_ALL_LINK_COMMAND)
def send_all_link_command(
    group: int, cmd1: int, cmd2: int, topic=pub.AUTO_TOPIC
) -> Outbound:
    """Create a SEND_ALL_LINK_COMMAND outbound message."""
    _create_outbound_message(group=group, cmd1=cmd1, cmd2=cmd2, topic=topic, priority=3)


def _create_flags(topic, extended):
    msg_type = topic_to_message_type(topic)
    return create_flags(msg_type, extended=extended)


@topic_to_message_handler(register_list=topic_register, topic=SEND_STANDARD)
def send_standard(
    address: Address,
    cmd1: int,
    cmd2: int,
    flags: MessageFlags = None,
    priority=5,
    topic=pub.AUTO_TOPIC,
) -> Outbound:
    """Create a SEND_STANDARD outbound message."""
    subtopics = topic.name.split(".")
    main_topic = subtopics[1]
    msg_type = None if len(subtopics) < 3 else subtopics[2]
    flags = flags if flags is not None else _create_flags(topic, False)
    kwargs = {"address": address, "flags": flags, "cmd1": cmd1, "cmd2": cmd2}
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_STD_SEND)
    send_topic = "send_message.{}".format(main_topic)
    if msg_type is not None:
        send_topic = "{}.{}".format(send_topic, msg_type)
    msg = Outbound(msg_def, **kwargs)
    publish_topic(send_topic, msg=msg, priority=priority)


@topic_to_message_handler(register_list=topic_register, topic=SEND_EXTENDED)
def send_extended(
    address: Address,
    cmd1: int,
    cmd2: int,
    user_data: UserData,
    flags: MessageFlags = None,
    priority=5,
    topic=pub.AUTO_TOPIC,
) -> Outbound:
    """Create a SEND_EXTENDED outbound message."""
    main_topic = topic.name.split(".")[1]
    flags = flags if flags is not None else _create_flags(topic, True)
    kwargs = {
        "address": address,
        "flags": flags,
        "cmd1": cmd1,
        "cmd2": cmd2,
        "user_data": user_data,
    }
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND)
    send_topic = "send_message.{}".format(main_topic)
    msg = Outbound(msg_def, **kwargs)
    publish_topic(send_topic, msg=msg, priority=priority)


@topic_to_message_handler(register_list=topic_register, topic=X10_SEND)
def x10_send(raw_x10: int, x10_flag: X10CommandType, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a X10_SEND outbound message."""
    _create_outbound_message(raw_x10=raw_x10, x10_flag=x10_flag, topic=topic)


@topic_to_message_handler(register_list=topic_register, topic=START_ALL_LINKING)
def start_all_linking(mode: AllLinkMode, group: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a START_ALL_LINKING outbound message."""
    _create_outbound_message(mode=mode, group=group, topic=topic, priority=7)


@topic_to_message_handler(register_list=topic_register, topic=CANCEL_ALL_LINKING)
def cancel_all_linking(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a CANCEL_ALL_LINKING outbound message."""
    _create_outbound_message(topic=topic, priority=7)


@topic_to_message_handler(register_list=topic_register, topic=SET_HOST_DEV_CAT)
def set_host_dev_cat(
    cat: DeviceCategory, subcat: int, firmware: int, topic=pub.AUTO_TOPIC
) -> Outbound:
    """Create a SET_HOST_DEV_CAT outbound message."""
    _create_outbound_message(
        cat=cat, subcat=subcat, firmware=firmware, topic=topic, priority=7
    )


@topic_to_message_handler(register_list=topic_register, topic=RESET_IM)
def reset_im(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a RESET_IM outbound message."""
    _create_outbound_message(topic=topic, priority=2)


@topic_to_message_handler(register_list=topic_register, topic=SET_ACK_MESSAGE_BYTE)
def set_ack_message_byte(cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_ACK_MESSAGE_BYTE outbound message."""
    _create_outbound_message(cmd2=cmd2, topic=topic, priority=7)


@topic_to_message_handler(register_list=topic_register, topic=GET_FIRST_ALL_LINK_RECORD)
def get_first_all_link_record(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_FIRST_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(topic=topic, priority=1)


@topic_to_message_handler(register_list=topic_register, topic=GET_NEXT_ALL_LINK_RECORD)
def get_next_all_link_record(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_NEXT_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(topic=topic, priority=1)


@topic_to_message_handler(register_list=topic_register, topic=SET_IM_CONFIGURATION)
def set_im_configuration(
    disable_auto_linking: bool,
    monitor_mode: bool,
    auto_led: bool,
    deadman: bool,
    topic=pub.AUTO_TOPIC,
) -> Outbound:
    """Create a SET_IM_CONFIGURATION outbound message."""
    flag_byte = 0x00
    flag_byte = flag_byte | (1 if disable_auto_linking else 0) << 7
    flag_byte = flag_byte | (1 if monitor_mode else 0) << 6
    flag_byte = flag_byte | (1 if auto_led else 0) << 5
    flag_byte = flag_byte | (1 if deadman else 0) << 4
    flags = IMConfigurationFlags(flag_byte)
    _create_outbound_message(flags=flags, topic=topic, priority=2)


@topic_to_message_handler(
    register_list=topic_register, topic=GET_ALL_LINK_RECORD_FOR_SENDER
)
def get_all_link_record_for_sender(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_ALL_LINK_RECORD_FOR_SENDER outbound message."""
    _create_outbound_message(topic=topic, priority=2)


@topic_to_message_handler(register_list=topic_register, topic=LED_ON)
def led_on(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a LED_ON outbound message."""
    _create_outbound_message(topic=topic, priority=7)


@topic_to_message_handler(register_list=topic_register, topic=LED_OFF)
def led_off(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a LED_OFF outbound message."""
    _create_outbound_message(topic=topic, priority=7)


@topic_to_message_handler(register_list=topic_register, topic=MANAGE_ALL_LINK_RECORD)
def manage_all_link_record(
    action: ManageAllLinkRecordAction,
    flags: AllLinkRecordFlags,
    group: int,
    target: Address,
    data1: int,
    data2: int,
    data3: int,
    topic=pub.AUTO_TOPIC,
) -> Outbound:
    """Create a MANAGE_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(
        action=action,
        flags=flags,
        group=group,
        target=target,
        data1=data1,
        data2=data2,
        data3=data3,
        topic=topic,
        priority=10,
    )


@topic_to_message_handler(register_list=topic_register, topic=SET_NAK_MESSAGE_BYTE)
def set_nak_message_byte(cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_NAK_MESSAGE_BYTE outbound message."""
    _create_outbound_message(cmd2=cmd2, topic=topic, priority=10)


@topic_to_message_handler(register_list=topic_register, topic=SET_ACK_MESSAGE_TWO_BYTES)
def set_ack_message_two_bytes(cmd1: int, cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_ACK_MESSAGE_TWO_BYTES outbound message."""
    _create_outbound_message(cmd1=cmd1, cmd2=cmd2, topic=topic, priority=10)


@topic_to_message_handler(register_list=topic_register, topic=RF_SLEEP)
def rf_sleep(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a RF_SLEEP outbound message."""
    _create_outbound_message(topic=topic, priority=2)


@topic_to_message_handler(register_list=topic_register, topic=GET_IM_CONFIGURATION)
def get_im_configuration(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_IM_CONFIGURATION outbound message."""
    _create_outbound_message(topic=topic, priority=7)
