"""Insteon Messages."""
from .message_definition import MessageDefinition
from ..constants import MESSAGE_START_CODE
class MessageBase():
    """Base class for all message classes."""

    def __init__(self, msg_def: MessageDefinition, **kwargs):
        """Initialize the MessageBase class."""
        self.start_code = MESSAGE_START_CODE
        self.message_id = msg_def.message_id
        for field in msg_def.fields:
            val = kwargs.get(field.name)
            val = val if val is None else field.type(val)
            setattr(self, field.name, val)
