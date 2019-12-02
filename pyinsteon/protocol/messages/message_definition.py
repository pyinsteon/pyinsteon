"""Class to define the message definitions."""


class MessageDefinition:
    """Insteon message defintion."""

    def __init__(self, message_id, message_fields: []):
        """Init the MessageDefinition class."""
        self._message_id = message_id
        self._fields = message_fields

    def __len__(self):
        """Emit the message length."""
        length = 2
        for field in self._fields:
            length += field.length
        return length

    @property
    def message_id(self):
        """Emit the message type."""
        return self._message_id

    @property
    def fields(self):
        """Emit the message fields."""
        return self._fields
