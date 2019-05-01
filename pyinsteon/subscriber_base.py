"""Base class for all subscribable classes."""
from abc import ABC
from typing import Callable

class SubscriberBase(ABC):
    """Event class to manage triggering of events.

    TODO: Use weak references.
    """

    def __init__(self):
        """Init the Event class."""
        self._subscribers = []

    def subscribe(self, callback: Callable):
        """Subscribe to the event."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback):
        """Unsubscribe to the event."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _call_subscribers(self, **kwargs):
        """Call subscribers to the event."""
        for subscriber in self._subscribers:
            subscriber(**kwargs)
