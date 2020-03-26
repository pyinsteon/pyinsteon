"""Inbound message handler."""

from abc import ABCMeta

from ..subscriber_base import SubscriberBase
from ..utils import build_topic


class InboundHandlerBase(SubscriberBase):
    """Inbound message handler."""

    __meta__ = ABCMeta

    def __init__(self, topic, address=None, group=None, message_type=None):
        """Init the InboundHandlerBase class."""
        subscriber_topic = build_topic(
            prefix="handler",
            topic=topic,
            address=address,
            group=group,
            message_type=message_type,
        )
        self._topic = topic
        super().__init__(subscriber_topic=subscriber_topic)
        for attr_str in dir(self):
            attr = getattr(self, attr_str)
            if hasattr(attr, "register_topic"):
                attr.register_topic(
                    attr, topic, address=address, group=group, message_type=message_type
                )
            if hasattr(attr, "register_status") and hasattr(self, "_address"):
                # pylint: disable=no-member
                attr.register_status(attr, self._address.id)
