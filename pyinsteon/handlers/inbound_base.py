"""Inbound message handler."""

from abc import ABC, abstractmethod
from typing import Callable
from .. import pub

class InboundHandlerBase(ABC):
    """Inbound message handler."""

    def __init__(self, topic: str):
        """Init the InboundHandlerBase class."""
        pub.subscribe(self.handler, topic)
        self._subscribers = []

    @abstractmethod
    def handler(self, **kwargs):
        """Handle the inbound message"""

    def subscribe(self, callback: Callable):
        """Subscribe to this message handler."""
        self._subscribers.append(callback)
