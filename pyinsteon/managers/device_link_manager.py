"""Manages links between devices to identify device state of responders."""
import asyncio
from .. import pub
from ..address import Address
from ..topics import (
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_CONTROLLER_REMOVED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from ..constants import MessageFlagType


def _controller_group_topic(responder, group):
    return "{}.{}".format(responder.id, group)


def _topic_to_addr_group(topic):
    elements = topic.name.split(".")
    try:
        address = Address(elements[0])
        group = int(elements[1])
        msg_type = getattr(MessageFlagType, elements[-1].upper())
    except [KeyError, TypeError]:
        return None, None
    return address, group, msg_type


class DeviceLinkManager:
    """Manages links between devices to identify state of responders."""

    def __init__(self):
        """Init the DeviceLinkManager class."""
        pub.subscribe(self._controller_link_created, DEVICE_LINK_CONTROLLER_CREATED)
        pub.subscribe(self._responder_link_created, DEVICE_LINK_RESPONDER_CREATED)
        pub.subscribe(self._controller_link_removed, DEVICE_LINK_CONTROLLER_REMOVED)
        pub.subscribe(self._responder_link_removed, DEVICE_LINK_RESPONDER_REMOVED)
        self._responders = {}

    def _controller_link_created(self, controller, responder, group):
        controller_group = _controller_group_topic(controller, group)
        try:
            topic = pub.getDefaultTopicMgr().getTopic(controller_group)
        except pub.TopicNameError:
            topic = None
        if not topic or (
            not pub.isSubscribed(self._check_responder, controller_group)
            and not pub.isSubscribed(self._check_controller, controller_group)
        ):
            pub.subscribe(self._check_controller, controller_group)

    def _responder_link_created(self, controller, responder, group):
        controller_group = _controller_group_topic(controller, group)
        try:
            topic = pub.getDefaultTopicMgr().getTopic(controller_group)
        except pub.TopicNameError:
            topic = None
        if topic and pub.isSubscribed(self._check_controller, controller_group):
            pub.unsubscribe(self._check_controller, controller_group)
        if not topic or not pub.isSubscribed(self._check_responder, controller_group):
            pub.subscribe(self._check_responder, controller_group)

        if self._responders.get(controller) is None:
            self._responders[controller] = {}
        if self._responders[controller].get(group) is None:
            self._responders[controller][group] = []
        self._responders[controller][group].append(responder)

    def _controller_link_removed(self, controller, responder, group):
        controller_group = _controller_group_topic(controller, group)
        try:
            topic = pub.getDefaultTopicMgr().getTopic(controller_group)
        except pub.TopicNameError:
            topic = None
        if topic and pub.isSubscribed(self._check_controller, controller_group):
            pub.subscribe(self._check_controller, controller_group)

    def _responder_link_removed(self, controller, responder, group):
        controller_group = _controller_group_topic(controller, group)
        try:
            topic = pub.getDefaultTopicMgr().getTopic(controller_group)
        except pub.TopicNameError:
            topic = None
        if topic and pub.isSubscribed(self._check_responder, controller_group):
            pub.subscribe(self._check_responder, controller_group)

        groups = self._responders.get(controller)
        if groups and groups.get(group):
            groups[group].remove(responder)

    def _check_responder(self, on_level, topic=pub.AUTO_TOPIC):
        from .. import devices

        controller, group, msg_type = _topic_to_addr_group(topic)
        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        groups = self._responders.get(controller)
        if groups:
            responder = groups.get(group)
            if group:
                devices[responder].states[group].set_value(on_level)
                asyncio.ensure_future(devices[responder].async_status())

    @classmethod
    def _check_controller(cls, on_level, topic=pub.AUTO_TOPIC):
        from .. import devices

        controller, group, msg_type = _topic_to_addr_group(topic)
        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        if controller is None or group is None:
            return
        for responder in devices[controller].aldb.get_responders(group):
            asyncio.ensure_future(devices[responder].async_status())
