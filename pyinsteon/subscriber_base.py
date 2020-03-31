"""Base class for all subscribable classes."""
import logging
from abc import ABC
from typing import Callable

from .utils import publish_topic, subscribe_topic, unsubscribe_topic

_LOGGER = logging.getLogger(__name__)


class SubscriberBase(ABC):
    """Event class to manage triggering of events."""

    def __init__(self, subscriber_topic):
        """Init the Event class."""
        self._subscriber_topic = subscriber_topic
        self._subscribers = []

    def subscribe(self, callback: Callable, force_strong_ref=False):
        """Subscribe to the event."""
        if force_strong_ref and callback not in self._subscribers:
            _LOGGER.debug("Adding subscriber to persistant list")
            self._subscribers.append(callback)
        subscribe_topic(callback, self._subscriber_topic, _LOGGER)

    def unsubscribe(self, callback):
        """Unsubscribe to the event."""
        unsubscribe_topic(callback, self._subscriber_topic)

    def _call_subscribers(self, **kwargs):
        """Call subscribers to the event."""
        publish_topic(self._subscriber_topic, **kwargs)
