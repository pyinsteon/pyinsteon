"""Inbound message handler."""

from abc import ABCMeta
from ..subscriber_base import SubscriberBase


class InboundHandlerBase(SubscriberBase):
    """Inbound message handler."""

    def __init__(self, topic):
        """Init the InboundHandlerBase class."""
        super().__init__()
        self._topic = topic
        for attr_str in dir(self):
            attr = getattr(self, attr_str)
            if hasattr(attr, 'register_topic'):
                attr.register_topic(attr, self._topic)
            if hasattr(attr, 'register_status') and hasattr(self, '_address'):
                #pylint: disable=no-member
                attr.register_status(attr, self._address)
