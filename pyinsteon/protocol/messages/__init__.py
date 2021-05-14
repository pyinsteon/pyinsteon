"""Insteon Messages."""
from ...constants import MESSAGE_START_CODE
from ...utils import vars_to_bytes, vars_to_repr, vars_to_string
from .message_definition import MessageDefinition


class MessageBase:
    """Base class for all message classes."""

    def __init__(self, msg_def: MessageDefinition, **kwargs):
        """Initialize the MessageBase class."""
        self._start_code = MESSAGE_START_CODE
        self._message_id = msg_def.message_id
        self._fields = msg_def.fields
        for field in self._fields:
            val = kwargs.get(field.name)
            if val is not None and isinstance(val, field.type):
                val = field.type(val)
            setattr(self, field.name, val)

    def __repr__(self):
        """Emit the message in a debug representation."""
        flds = []
        flds.append(("msg_id", self.message_id))
        for field in self._fields:
            flds.append((field.name, getattr(self, field.name)))
        return vars_to_repr(flds)

    def __bytes__(self):
        """Emit the message bytes."""
        data = []
        data.append(self.start_code)
        data.append(self.message_id)
        for field in self._fields:
            data.append(getattr(self, field.name))
        return vars_to_bytes(data)

    def __str__(self):
        """Emit the message as a string."""
        flds = []
        flds.append(("msg_id", self.message_id))
        for field in self._fields:
            flds.append((field.name, getattr(self, field.name)))
        return vars_to_string(flds)

    @property
    def start_code(self):
        """Return message start code 0x02."""
        return self._start_code

    @property
    def message_id(self):
        """Return the message ID."""
        return self._message_id

    @property
    def fields(self):
        """Return the fields contained in the message."""
        return self._fields
