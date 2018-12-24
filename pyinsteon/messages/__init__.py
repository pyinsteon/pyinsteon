"""Insteon Messages."""
import logging

from ..address import Address
from ..constants import MessageId
from .inbound_message import InboundMessage
from .message_definions import INBOUND_MESSAGE_DEFINITIONS
from .message_flags import MessageFlags


_LOGGER = logging.getLogger(__name__)


def create_from_raw_data(raw_data: bytearray) -> InboundMessage:
    """Create a message from a raw byte array."""

    def _create_message(fields, raw_data):
        msg_len = 2
        for field in msg_def.fields:
            msg_len += field.length
        if len(raw_data) >= msg_len:
            return InboundMessage(fields, raw_data)
        _LOGGER.debug("Message too short")
        return None

    def _standard_message(raw_data):
        from .message_definions import FLD_STD_REC, FLD_EXT_REC
        msg = _create_message(FLD_STD_REC, raw_data)
        # pylint: disable=E1101
        if msg.flags.is_extended:
            msg = _create_message(FLD_EXT_REC, raw_data)
        return msg

    _LOGGER.info("Starting create")
    if len(raw_data) < 2:
        _LOGGER.debug('Message less than 2 bytes')
        return None

    for msg_def in INBOUND_MESSAGE_DEFINITIONS:
        if msg_def.type.value == raw_data[1]:
            if msg_def.type.value == 0x50:
                return _standard_message(raw_data)
            return _create_message(msg_def.fields, raw_data)

    _LOGGER.debug("Message ID not found")
    return None

