"""Insteon message data structure defintion."""
from binascii import hexlify
from enum import IntEnum
import logging

from ..address import Address
from .all_link_record_flags import AllLinkRecordFlags
from ..constants import MessageId
from .message_definions import INBOUND_MESSAGE_DEFINITIONS
from .message_flags import MessageFlags
from .user_data import UserData


_LOGGER = logging.getLogger(__name__)


def create(raw_data: bytearray):
    """Create a message from a raw byte array."""

    def _create_message(fields, raw_data):
        msg_len = 2
        for field in msg_def.fields:
            msg_len += field.length
        if len(raw_data) >= msg_len:
            return Inbound(fields, raw_data)
        _LOGGER.debug("Message too short")
        return None

    def _standard_message(raw_data):
        from .message_definions import FLD_STD_SEND_ACK, FLD_EXT_SEND_ACK
        msg = _create_message(FLD_STD_SEND_ACK, raw_data)
        # pylint: disable=E1101
        if msg.flags.is_extended:
            msg = _create_message(FLD_EXT_SEND_ACK, raw_data)
        return msg

    _LOGGER.info("Starting create")
    if len(raw_data) < 2:
        _LOGGER.debug('Message less than 2 bytes')
        return None

    for msg_def in INBOUND_MESSAGE_DEFINITIONS:
        if msg_def.type.value == raw_data[1]:
            if msg_def.type.value == MessageId.SEND_STANDARD.value:
                return _standard_message(raw_data)
            return _create_message(msg_def.fields, raw_data)

    _LOGGER.debug("Message ID not found")
    return None


class Inbound():
    """Insteon inbound message data definition."""

    def __init__(self, fields, data):
        """Init the Inbound message class."""
        self._fields = fields
        _slices = self._create_slices(fields)
        self.start_code = data[0]
        self.id = MessageId(data[1])
        self._len = 2
        curr_slice = 2
        for field in fields:
            val = field.type(data[_slices[curr_slice]])
            _LOGGER.debug('slice: %s', _slices[curr_slice])
            _LOGGER.debug('Field %s value %s', field.name, val)
            setattr(self, field.name, val)
            self._len += field.length
            curr_slice += 1

    def __repr__(self):
        """Emit the message as a dict."""
        cls_repr = {}
        cls_repr['id'] = '{2:x}'.format(self.id)
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

    def _create_slices(self, fields):
        slices = []
        slices.append(slice(0, 1))
        slices.append(slice(1, 2))
        start = 2
        for field in fields:
            stop = start + field.length
            if field.length > 1:
                slices.append(slice(start, stop))
            else:
                slices.append(start)
            start = stop
        return slices

    def __bytes__(self):
        """Emit the message bytes."""
        from ..utils import vars_to_bytes
        data = []
        data.append(self.start_code)
        data.append(self.id)
        for field in self._fields:
            data.append(getattr(self, field.name))
        return vars_to_bytes(data)

    def __str__(self):
        """Emit the message in hex."""
        return hexlify(bytes(self)).decode()
