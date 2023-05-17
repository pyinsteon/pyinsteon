"""Base class for all subscribable classes."""
from abc import ABC
import logging
from typing import Callable

from . import pub
from .utils import publish_topic, subscribe_topic, unsubscribe_topic

_LOGGER = logging.getLogger(__name__)


class SubscriberBase(ABC):
    """Event class to manage triggering of events."""

    arg_spec = {}
    required_args = None  # Default sets all arg_spec as required

    def __init__(self, subscriber_topic):
        """Init the Event class."""
        self._subscriber_topic = subscriber_topic
        self._subscribers = []
        if self.arg_spec:
            topic = pub.getDefaultTopicMgr().getOrCreateTopic(self._subscriber_topic)
            if not topic.hasMDS():
                if self.required_args is not None:
                    required_args = self.required_args
                else:
                    required_args = list(self.arg_spec)
                topic.setMsgArgSpec(self.arg_spec, required_args)

    @property
    def topic(self):
        """Return the subscriber topic."""
        return self._subscriber_topic

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
