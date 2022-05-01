"""Insteon inbound message data structure defintion."""
import logging
from binascii import hexlify
from typing import Tuple

from ...constants import MessageId
from ...data_types.message_flags import MessageFlags
from . import MessageBase
from .message_definition import MessageDefinition
from .message_definitions import FLD_EXT_SEND_ACK, INBOUND_MSG_DEF

_LOGGER = logging.getLogger(__name__)


def trim_data(raw_data: bytearray):
    """Trim bad data from the front of a message byte stream."""
    data_bytes = bytes(raw_data)
    while data_bytes and data_bytes[0] != 0x02:
        data_bytes = data_bytes[1:]
    return data_bytes


class Inbound(MessageBase):
    """Insteon inbound message data definition."""

    def __init__(self, msg_def: MessageDefinition, raw_data: bytearray):
        """Init the Inbound message class."""
        self._fields = msg_def.fields
        self._len = len(msg_def)
        field_vals = self._slice_data(msg_def.slices, raw_data)
        super().__init__(msg_def, **field_vals)

    def __len__(self):
        """Emit the length of the message."""
        return self._len

    def _slice_data(self, slices, raw_data):
        curr_slice = 2
        field_vals = {}
        for field in self._fields:
            val = field.type(raw_data[slices[curr_slice]])
            field_vals[field.name] = val
            curr_slice += 1
        return field_vals

    def __str__(self):
        """Emit the message in hex."""
        return hexlify(bytes(self)).decode()


def create(raw_data: bytearray) -> Tuple[Inbound, bytearray]:
    """Create a message from a raw byte array."""

    def _remaining_data(msg, data_bytes):
        if msg is not None:
            return data_bytes[len(msg) :]
        return data_bytes

    def _create_message(msg_def, data_bytes):
        msg = Inbound(msg_def, data_bytes)
        return msg, _remaining_data(msg, data_bytes)

    def _standard_message(data_bytes):
        flag_byte = 5
        flags = MessageFlags(data_bytes[flag_byte])
        if flags.is_extended:
            msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND_ACK)
            if len(data_bytes) < len(msg_def):
                _LOGGER.debug("Full extended message not received")
                _LOGGER.debug("Returning: %s", data_bytes.hex())
                return None, bytearray(data_bytes)
        else:
            msg_def = INBOUND_MSG_DEF.get(MessageId.SEND_STANDARD)
        msg, remaining_data = _create_message(msg_def, data_bytes)
        return msg, remaining_data

    _LOGGER.debug("IN CREATE: %s", raw_data.hex())
    data_bytes = trim_data(raw_data)
    if len(data_bytes) < 2:
        _LOGGER.debug("Message less than 2 bytes")
        _LOGGER.debug("Returning: %s", data_bytes.hex())
        return None, bytearray(data_bytes)
    try:
        msg_id = MessageId(data_bytes[1])
    except ValueError as err:
        _LOGGER.debug("Error: %s", err)
        truncate = 1 if data_bytes[1] == 0x02 else 2
        data_bytes = trim_data(bytearray(data_bytes[truncate:]))
        _LOGGER.debug("Returning: %s", data_bytes.hex())
        return None, bytearray(data_bytes)
    msg_def = INBOUND_MSG_DEF.get(msg_id)
    if msg_def is not None:
        if len(data_bytes) < len(msg_def):
            _LOGGER.debug("Full message not received")
            _LOGGER.debug("Returning: %s", data_bytes.hex())
            return None, bytearray(data_bytes)

        if msg_id == MessageId.SEND_STANDARD:
            msg, remaining_data = _standard_message(data_bytes)
        else:
            msg, remaining_data = _create_message(msg_def, data_bytes)
        _LOGGER.debug("Returning: %s", remaining_data.hex())
        return msg, bytearray(remaining_data)
    return None, trim_data(data_bytes[1:])
