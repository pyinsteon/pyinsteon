"""Base class for all subscribable classes."""
from abc import ABC
from typing import Callable
from . import pub


class SubscriberBase(ABC):
    """Event class to manage triggering of events."""

    def __init__(self, subscriber_topic):
        """Init the Event class."""
        self._subscriber_topic = subscriber_topic

    def subscribe(self, callback: Callable):
        """Subscribe to the event."""
        topic_mgr = pub.getDefaultTopicMgr()
        topic = topic_mgr.getOrCreateTopic(self._subscriber_topic)
        if not pub.isSubscribed(callback, topicName=topic.name):
            pub.subscribe(callback, topicName=topic.name)

    def unsubscribe(self, callback):
        """Unsubscribe to the event."""
        pub.unsubscribe(callback, topicName=self._subscriber_topic)

    def _call_subscribers(self, **kwargs):
        """Call subscribers to the event."""
        pub.sendMessage(topicName=self._subscriber_topic, **kwargs)
