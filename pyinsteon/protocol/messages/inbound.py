"""Insteon inbound message data structure defintion."""
import logging
from binascii import hexlify

from . import MessageBase
from ...constants import MessageId
from .message_definition import MessageDefinition
from .message_definitions import FLD_EXT_SEND_ACK, FLD_STD_SEND_ACK, INBOUND_MSG_DEF
from .message_flags import MessageFlags

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

        slices = self._create_slices()
        field_vals = self._slice_data(slices, raw_data)
        super().__init__(msg_def, **field_vals)

    def __len__(self):
        """Emit the length of the message."""
        return self._len

    def _create_slices(self):
        slices = []
        slices.append(slice(0, 1))
        slices.append(slice(1, 2))
        start = 2
        for field in self._fields:
            stop = start + field.length
            if field.length > 1:
                slices.append(slice(start, stop))
            else:
                slices.append(start)
            start = stop
        return slices

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


def create(raw_data: bytearray) -> (Inbound, bytearray):
    """Create a message from a raw byte array."""

    def _remaining_data(msg, raw_data):
        if msg is not None:
            return raw_data[len(msg) :]
        return raw_data

    def _create_message(msg_def, raw_data):
        msg_len = 2
        for field in msg_def.fields:
            msg_len += field.length
        if len(raw_data) >= msg_len:
            msg = Inbound(msg_def, raw_data)
            return msg, _remaining_data(msg, raw_data)
        _LOGGER.debug("Message too short")
        return None, raw_data

    def _standard_message(raw_data):
        flag_byte = 5
        flags = MessageFlags(raw_data[flag_byte])
        if flags.is_extended:
            msg_def = MessageDefinition(MessageId.SEND_EXTENDED, FLD_EXT_SEND_ACK)
            msg, remaining_data = _create_message(msg_def, raw_data)
        else:
            msg_def = MessageDefinition(MessageId.SEND_STANDARD, FLD_STD_SEND_ACK)
            msg, remaining_data = _create_message(msg_def, raw_data)
        return msg, remaining_data

    _LOGGER.debug("IN CREATE: %s", raw_data.hex())
    data_bytes = trim_data(raw_data)
    if len(data_bytes) < 2:
        _LOGGER.debug("Message less than 2 bytes")
        return None, raw_data
    try:
        msg_id = MessageId(data_bytes[1])
        msg_def = INBOUND_MSG_DEF.get(msg_id)
        if msg_def is not None:
            if len(data_bytes) < len(msg_def):
                _LOGGER.debug("Full message not received")
                return None, raw_data
            if msg_def.message_id == MessageId.SEND_STANDARD:
                msg, remaining_data = _standard_message(data_bytes)
            else:
                msg, remaining_data = _create_message(msg_def, data_bytes)
            return msg, bytearray(remaining_data)
    except ValueError:
        _LOGGER.debug("Message ID not found: 0x%02x", data_bytes[1])
        _LOGGER.debug("Bad Data: %s", raw_data.hex())
        truncate = 1 if data_bytes[1] == 0x02 else 2
        return None, bytearray(data_bytes[truncate:])

    return None, raw_data
