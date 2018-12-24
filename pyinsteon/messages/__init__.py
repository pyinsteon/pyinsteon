"""Insteon Messages."""
from collections import namedtuple
import logging

from ..address import Address
from ..constants import MessageCode
from .inbound_message import InboundMessage
from .message_flags import MessageFlags


_LOGGER = logging.getLogger(__name__)


def create_from_raw_data(raw_data: bytearray) -> InboundMessage:
    """Create a message from a raw byte array."""
    _LOGGER.info("Starting create")
    if len(raw_data) < 2:
        _LOGGER.debug('Message less than 2 bytes')
        return None

    for msg_def in INBOUND_MESSAGE_DEFINITIONS:
        if msg_def.type.value == raw_data[1]:
            msg_len = 2
            for field in msg_def.fields:
                msg_len += field.length
            if len(raw_data) >= msg_len:
                return InboundMessage(msg_def.fields, raw_data)
            _LOGGER.debug("Message too short")
            return None
    _LOGGER.debug("Message type not found")
    return None

MessageDataField = namedtuple("MessageDataField", "name length type")


MessageDefinition = namedtuple("MessageDefinition", "type fields")


INBOUND_MESSAGE_DEFINITIONS = [
    MessageDefinition(MessageCode.STANDARD_RECEIVED,
                      [MessageDataField("address", 3, Address),
                       MessageDataField("target", 3, Address),
                       MessageDataField("flags", 1, MessageFlags),
                       MessageDataField("cmd1", 1, int),
                       MessageDataField("cmd2", 1, int)])]
