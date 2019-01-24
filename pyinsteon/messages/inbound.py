"""Insteon inbound message data structure defintion."""
from binascii import hexlify
from enum import IntEnum
import logging

from ..address import Address
from .all_link_record_flags import AllLinkRecordFlags
from ..constants import MessageId
from . import MessageBase
from .message_definition import MessageDefinition
from .message_definitions import INBOUND_MSG_DEF
from .message_flags import MessageFlags
from .user_data import UserData


_LOGGER = logging.getLogger(__name__)


def create(raw_data: bytearray):
    """Create a message from a raw byte array."""

    def _remaining_data(msg, raw_data):
        if msg is not None:
            return raw_data[len(msg):]
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
        from .message_definitions import FLD_STD_SEND_ACK, FLD_EXT_SEND_ACK
        msg_def = MessageDefinition(MessageId.SEND_STANDARD, FLD_STD_SEND_ACK)
        msg, remaining_data = _create_message(msg_def, raw_data)
        # pylint: disable=E1101
        if msg.flags.is_extended:
            msg_def = MessageDefinition(MessageId.SEND_STANDARD,
                                        FLD_EXT_SEND_ACK)
            msg, remaining_data = _create_message(msg_def, raw_data)
        return msg, remaining_data

    _LOGGER.info("Starting create")
    if len(raw_data) < 2:
        _LOGGER.debug('Message less than 2 bytes')
        return None, raw_data

    msg_id = MessageId(raw_data[1])
    msg_def = INBOUND_MSG_DEF.get(msg_id)
    if msg_def is not None:
        if msg_def.message_id == MessageId.SEND_STANDARD:
            msg, remaining_data = _standard_message(raw_data)
        else:
            msg, remaining_data = _create_message(msg_def, raw_data)
        return msg, remaining_data

    _LOGGER.debug("Message ID not found")
    return None, raw_data


class Inbound(MessageBase):
    """Insteon inbound message data definition."""

    def __init__(self, msg_def: MessageDefinition, raw_data: bytearray):
        """Init the Inbound message class."""
        self._fields = msg_def.fields
        # self.start_code = raw_data[0]
        # self.message_id = msg_def.message_id
        self._len = len(msg_def)

        slices = self._create_slices()
        field_vals = self._slice_data(slices, raw_data)
        super().__init__(msg_def, **field_vals)

    def __repr__(self):
        """Emit the message as a dict."""
        cls_repr = {}
        cls_repr['id'] = '{2:x}'.format(self.message_id)
        for fld in self._fields:
            val = getattr(self, fld.name)
            val_bytes = b''
            if isinstance(val, [int, IntEnum]):
                val_bytes = bytes([val])
            elif isinstance(val, [bytes, Address, MessageFlags,
                                  AllLinkRecordFlags, UserData]):
                val_bytes = bytes(val)
            cls_repr[fld.name] = hexlify(val_bytes).decode()
        return str(cls_repr)

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
            _LOGGER.debug('slice: %s', slices[curr_slice])
            _LOGGER.debug('Field %s value %s', field.name, val)
            field_vals[field.name] = val
            curr_slice += 1
        return field_vals

    def __bytes__(self):
        """Emit the message bytes."""
        from ..utils import vars_to_bytes
        data = []
        data.append(self.start_code)
        data.append(self.message_id)
        for field in self._fields:
            data.append(getattr(self, field.name))
        return vars_to_bytes(data)

    def __str__(self):
        """Emit the message in hex."""
        return hexlify(bytes(self)).decode()
