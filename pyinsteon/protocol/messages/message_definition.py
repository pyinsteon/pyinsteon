"""Class to define the message definitions."""
from typing import List

from ...constants import MessageId


def _calc_length(fields):
    """Calculate the length."""
    length = 2
    for field in fields:
        if isinstance(field, MessageDefinition):
            continue
        length += field.length
    return length


def _create_slices(fields):
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


class MessageDefinition:
    """Insteon message defintion."""

    def __init__(
        self,
        message_id: MessageId,
        topic: str,
        message_fields: List,
        modem_topic: bool = True,
    ):
        """Init the MessageDefinition class."""
        self._modem_topic = modem_topic
        self._topic = topic
        self._message_id = message_id
        self._fields = message_fields
        self._length = _calc_length(message_fields)
        self._slices = _create_slices(self.fields)

    def __len__(self):
        """Emit the message length."""
        return self._length

    @property
    def topic(self) -> str:
        """Emit the message topic."""
        return self._topic

    @property
    def modem_topic(self):
        """Emit the modem relevance  of this topic."""
        return self._modem_topic

    @property
    def message_id(self):
        """Emit the message type."""
        return self._message_id

    @property
    def fields(self):
        """Emit the message fields."""
        return self._fields

    @property
    def slices(self):
        """Emit the message slices."""
        return self._slices
