"""Inbound message handler."""

from abc import ABCMeta

from ..address import Address
from ..constants import MessageFlagType
from ..subscriber_base import SubscriberBase
from ..utils import build_topic


class InboundHandlerBase(SubscriberBase):
    """Inbound message handler."""

    __meta__ = ABCMeta

    def __init__(self, topic, address=None, group=None, message_type=None):
        """Init the InboundHandlerBase class."""

        self._topic = topic
        if message_type is not None:
            self._message_type = MessageFlagType(message_type)
        else:
            self._message_type = None
        self._group = int(group) if group is not None else None
        self._address = Address(address) if address is not None else None
        subscriber_topic = build_topic(
            prefix="handler",
            topic=topic,
            address=address,
            group=group,
            message_type=message_type,
        )

        super().__init__(subscriber_topic=subscriber_topic)
        for attr_str in dir(self):
            attr = getattr(self, attr_str)
            if hasattr(attr, "register_handler"):
                attr.register_handler(
                    func=attr,
                    topic=topic,
                    address=address,
                    group=group,
                    message_type=message_type,
                )
            if hasattr(attr, "register_status"):
                # pylint: disable=no-member
                attr.register_status(attr, self._address.id)
