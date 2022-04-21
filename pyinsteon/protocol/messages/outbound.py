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
from ...data_types.all_link_record_flags import AllLinkRecordFlags
from ...data_types.im_config_flags import IMConfigurationFlags
from ...data_types.message_flags import MessageFlags
from ...data_types.user_data import UserData
from ...topics import (
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
    RESET_IM,
    RF_SLEEP,
    SEND_ALL_LINK_COMMAND,
    SEND_EXTENDED,
    SEND_STANDARD,
    SET_ACK_MESSAGE_BYTE,
    SET_ACK_MESSAGE_TWO_BYTES,
    SET_HOST_DEVICE_CATEGORY,
    SET_IM_CONFIGURATION,
    SET_NAK_MESSAGE_BYTE,
    START_ALL_LINKING,
    WRITE_EEPROM,
    X10_SEND,
)
from ...utils import subscribe_topic
from ..topic_converters import topic_to_message_handler, topic_to_message_type
from . import MessageBase
from .message_definition import MessageDefinition
from .message_definitions import FLD_EXT_SEND, FLD_STD_SEND, OUTBOUND_MSG_DEF

MESSAGE_REGISTER = {}

_LOGGER = logging.getLogger(__name__)


def register_outbound_handlers():
    """Register outbound handlers."""
    for topic, func in MESSAGE_REGISTER.items():
        subscribe_topic(func, topic)


class OutboundWriteManager:
    """Ourbound write manager."""

    def __init__(self):
        """Init the OutboundWriteManager class."""
        self._protocol_write = None

    @property
    def protocol_write(self):
        """Return the write method of the protocol."""
        return self._protocol_write

    @protocol_write.setter
    def protocol_write(self, value):
        """Set the write method of the protocol."""
        self._protocol_write = value

    def write(self, msg, priority):
        """Write to the protocol."""
        if self._protocol_write is None:
            raise AttributeError
        self._protocol_write(msg=msg, priority=priority)


outbound_write_manager = OutboundWriteManager()


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
    outbound_write_manager.write(msg=msg, priority=priority)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=GET_IM_INFO)
def get_im_info(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_IM_INFO outbound message."""
    _create_outbound_message(topic=topic, priority=1)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=SEND_ALL_LINK_COMMAND)
def send_all_link_command(
    group: int, cmd1: int, cmd2: int, topic=pub.AUTO_TOPIC
) -> Outbound:
    """Create a SEND_ALL_LINK_COMMAND outbound message."""
    _create_outbound_message(group=group, cmd1=cmd1, cmd2=cmd2, topic=topic, priority=3)


def _create_flags(topic, extended):
    msg_type = topic_to_message_type(topic)
    return MessageFlags.create(msg_type, extended=extended)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=SEND_STANDARD)
def send_standard(
    address: Address,
    cmd1: int,
    cmd2: int,
    flags: MessageFlags = None,
    priority=5,
    topic=pub.AUTO_TOPIC,
) -> Outbound:
    """Create a SEND_STANDARD outbound message."""
    flags = flags if flags is not None else _create_flags(topic, False)
    kwargs = {"address": address, "flags": flags, "cmd1": cmd1, "cmd2": cmd2}
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_STD_SEND)
    msg = Outbound(msg_def, **kwargs)
    outbound_write_manager.write(msg=msg, priority=priority)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=SEND_EXTENDED)
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
    flags = flags if flags is not None else _create_flags(topic, True)
    kwargs = {
        "address": address,
        "flags": flags,
        "cmd1": cmd1,
        "cmd2": cmd2,
        "user_data": user_data,
    }
    msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND)
    msg = Outbound(msg_def, **kwargs)
    outbound_write_manager.write(msg=msg, priority=priority)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=X10_SEND)
def x10_send(raw_x10: int, x10_flag: X10CommandType, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a X10_SEND outbound message."""
    _create_outbound_message(raw_x10=raw_x10, x10_flag=x10_flag, topic=topic)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=START_ALL_LINKING)
def start_all_linking(
    link_mode: AllLinkMode, group: int, topic=pub.AUTO_TOPIC
) -> Outbound:
    """Create a START_ALL_LINKING outbound message."""
    _create_outbound_message(link_mode=link_mode, group=group, topic=topic, priority=7)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=CANCEL_ALL_LINKING)
def cancel_all_linking(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a CANCEL_ALL_LINKING outbound message."""
    _create_outbound_message(topic=topic, priority=7)


@topic_to_message_handler(
    register_list=MESSAGE_REGISTER, topic=SET_HOST_DEVICE_CATEGORY
)
def set_host_device_category(
    cat: DeviceCategory, subcat: int, firmware: int, topic=pub.AUTO_TOPIC
) -> Outbound:
    """Create a SET_HOST_DEVICE_CATEGORY outbound message."""
    _create_outbound_message(
        cat=cat, subcat=subcat, firmware=firmware, topic=topic, priority=7
    )


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=RESET_IM)
def reset_im(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a RESET_IM outbound message."""
    _create_outbound_message(topic=topic, priority=2)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=SET_ACK_MESSAGE_BYTE)
def set_ack_message_byte(cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_ACK_MESSAGE_BYTE outbound message."""
    _create_outbound_message(cmd2=cmd2, topic=topic, priority=7)


@topic_to_message_handler(
    register_list=MESSAGE_REGISTER, topic=GET_FIRST_ALL_LINK_RECORD
)
def get_first_all_link_record(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_FIRST_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(topic=topic, priority=1)


@topic_to_message_handler(
    register_list=MESSAGE_REGISTER, topic=GET_NEXT_ALL_LINK_RECORD
)
def get_next_all_link_record(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_NEXT_ALL_LINK_RECORD outbound message."""
    _create_outbound_message(topic=topic, priority=1)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=SET_IM_CONFIGURATION)
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
    register_list=MESSAGE_REGISTER, topic=GET_ALL_LINK_RECORD_FOR_SENDER
)
def get_all_link_record_for_sender(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_ALL_LINK_RECORD_FOR_SENDER outbound message."""
    _create_outbound_message(topic=topic, priority=2)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=LED_ON)
def led_on(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a LED_ON outbound message."""
    _create_outbound_message(topic=topic, priority=7)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=LED_OFF)
def led_off(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a LED_OFF outbound message."""
    _create_outbound_message(topic=topic, priority=7)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=MANAGE_ALL_LINK_RECORD)
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


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=SET_NAK_MESSAGE_BYTE)
def set_nak_message_byte(cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_NAK_MESSAGE_BYTE outbound message."""
    _create_outbound_message(cmd2=cmd2, topic=topic, priority=10)


@topic_to_message_handler(
    register_list=MESSAGE_REGISTER, topic=SET_ACK_MESSAGE_TWO_BYTES
)
def set_ack_message_two_bytes(cmd1: int, cmd2: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a SET_ACK_MESSAGE_TWO_BYTES outbound message."""
    _create_outbound_message(cmd1=cmd1, cmd2=cmd2, topic=topic, priority=10)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=RF_SLEEP)
def rf_sleep(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a RF_SLEEP outbound message."""
    _create_outbound_message(topic=topic, priority=2)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=GET_IM_CONFIGURATION)
def get_im_configuration(topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a GET_IM_CONFIGURATION outbound message."""
    _create_outbound_message(topic=topic, priority=7)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=READ_EEPROM)
def read_eeprom(mem_hi: int, mem_low: int, topic=pub.AUTO_TOPIC) -> Outbound:
    """Create a READ_EEPROM outbound message."""
    _create_outbound_message(mem_hi=mem_hi, mem_low=mem_low, topic=topic, priority=10)


@topic_to_message_handler(register_list=MESSAGE_REGISTER, topic=WRITE_EEPROM)
def write_eeprom(
    mem_hi: int,
    mem_low: int,
    flags: AllLinkRecordFlags,
    group: int,
    target: Address,
    data1: int,
    data2: int,
    data3: int,
    topic=pub.AUTO_TOPIC,
) -> Outbound:
    """Create a WRITE_EEPROM outbound message."""
    _create_outbound_message(
        mem_hi=mem_hi,
        mem_low=mem_low,
        flags=flags,
        group=group,
        target=target,
        data1=data1,
        data2=data2,
        data3=data3,
        topic=topic,
        priority=10,
    )
