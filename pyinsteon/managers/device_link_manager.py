"""Manages links between devices to identify device state of responders."""
from pubsub.core.topicobj import Topic

from .. import pub
from ..address import Address
from ..constants import MessageFlagType
from ..topics import (
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from ..utils import subscribe_topic


def _controller_group_topic(controller, group) -> Topic:
    topic_str = f"{controller.id}.{group}"
    topic_mgr = pub.getDefaultTopicMgr()
    topic = topic_mgr.getOrCreateTopic(topic_str)
    return topic


def _topic_to_addr_group(topic):
    elements = topic.name.split(".")
    try:
        address = Address(elements[0])
        group = int(elements[1])
        msg_type = getattr(MessageFlagType, elements[-1].upper())
    except [KeyError, TypeError]:
        return None, None, None
    return address, group, msg_type


class DeviceLinkManager:
    """Manages links between devices to identify state of responders.

    Listens for broadcast messages from a device and identifies the responders of the device.
    Once the responders are identified, the state of the responders is determined.
    """

    # TODO: figure out how to remove responder records

    def __init__(self, devices):
        """Init the DeviceLinkManager class."""
        subscribe_topic(self._responder_link_created, DEVICE_LINK_CONTROLLER_CREATED)
        subscribe_topic(self._responder_link_created, DEVICE_LINK_RESPONDER_CREATED)
        subscribe_topic(self._responder_link_removed, DEVICE_LINK_RESPONDER_REMOVED)
        self._devices = devices
        # Dict of {address: {group: [address]}}
        self._controller_responders = {}

    @property
    def scenes(self):
        """Return a list of scenes."""
        return self._controller_responders.get(self._devices.modem.address, {})

    @property
    def links(self):
        """Return a list of device links."""
        return {
            controller: controller_groups
            for controller, controller_groups in self._controller_responders.items()
            if controller != self._devices.modem.address
        }

    def _responder_link_created(self, controller, responder, group):
        controller = Address(controller)
        responder = Address(responder)
        if responder == self._devices.modem.address or group == 0:
            return
        topic = _controller_group_topic(controller, group)
        subscribe_topic(self._async_check_responders, topic.name)
        controller_groups = self._controller_responders.get(controller, {})
        controller_group = controller_groups.get(group, [])
        if responder not in controller_group:
            controller_group.append(responder)
        controller_groups[group] = controller_group
        self._controller_responders[controller] = controller_groups

    def _responder_link_removed(self, controller, responder, group):
        """Remove a responder from the controller/responder list."""
        controller = Address(controller)
        responder = Address(responder)
        controller_groups = self._controller_responders.get(controller, {})
        if not controller_groups:
            return
        controller_group = controller_groups.get(group, [])
        if not controller_group:
            return
        if responder in controller_group:
            controller_group.remove(responder)

    async def _async_check_responders(self, topic=pub.AUTO_TOPIC, **kwargs):
        controller, group, msg_type = _topic_to_addr_group(topic)

        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        if group == 0:
            return
        known_responders = self._controller_responders.get(controller, {}).get(
            group, {}
        )

        for responder in known_responders:
            device = self._devices[responder]
            if device:
                # If the device is a category 1 or 2 device we can pre-load the device state with the
                # ALDB record data1 field value. We will then check the actual status later.
                if device.cat in [0x01, 0x02]:
                    for rec in device.aldb.find(group=group, target=controller):
                        button = rec.data3 if rec.data3 else 1
                        if button in device.groups:
                            device.groups[button].value = rec.data1
                if not device.is_battery:
                    await device.async_status()
