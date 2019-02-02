"""Insteon Messages."""
from .message_definition import MessageDefinition
from ..constants import MESSAGE_START_CODE
class MessageBase():
    """Base class for all message classes."""

    def __init__(self, msg_def: MessageDefinition, **kwargs):
        """Initialize the MessageBase class."""
        self._start_code = MESSAGE_START_CODE
        self._message_id = msg_def.message_id
        self._fields = msg_def.fields
        for field in self._fields:
            val = kwargs.get(field.name)
            val = val if val is None else field.type(val)
            setattr(self, field.name, val)

    def __bytes__(self):
        """Emit the message bytes."""
        from ..utils import vars_to_bytes
        data = []
        data.append(self.start_code)
        data.append(self.message_id)
        for field in self._fields:
            data.append(getattr(self, field.name))
        return vars_to_bytes(data)

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
