"""Inbound message handler."""

from abc import ABC
from typing import Callable


class InboundHandlerBase(ABC):
    """Inbound message handler."""

    def __init__(self, topic):
        """Init the InboundHandlerBase class."""
        self._topic = topic
        self._subscribers = []
        for attr_str in dir(self):
            attr = getattr(self, attr_str)
            if hasattr(attr, 'register_topic'):
                attr.register_topic(attr, self._topic)

    def subscribe(self, callback: Callable):
        """Subscribe to this message handler."""
        self._subscribers.append(callback)

    def _call_subscribers(self, **kwargs):
        """Call all subscribers."""
        for listener in self._subscribers:
            listener(**kwargs)
