"""Inbound message handler."""

from abc import ABCMeta
from ..subscriber_base import SubscriberBase


class InboundHandlerBase(SubscriberBase):
    """Inbound message handler."""

    __meta__ = ABCMeta

    def __init__(self, topic, subscriber_topic=None):
        """Init the InboundHandlerBase class."""
        if subscriber_topic is None:
            subscriber_topic = "subscriber.{}".format(topic)
        subscriber_topic = subscriber_topic.replace(".", "_")
        super().__init__(subscriber_topic=subscriber_topic)
        self._topic = topic
        for attr_str in dir(self):
            attr = getattr(self, attr_str)
            if hasattr(attr, "register_topic"):
                attr.register_topic(attr, self._topic)
            if hasattr(attr, "register_status") and hasattr(self, "_address"):
                # pylint: disable=no-member
                attr.register_status(attr, self._address)
