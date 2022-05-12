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
    topic = topic_mgr.getTopic(topic_str, okIfNone=True)
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
        self._controller_responders = {}

    def _responder_link_created(self, controller, responder, group):
        topic = _controller_group_topic(controller, group)
        if not topic.hasListener(self._async_check_responders):
            subscribe_topic(self._async_check_responders, topic.name)
        controller_responders = self._controller_responders.get(repr(controller), [])
        if repr(responder) not in controller_responders:
            controller_responders.append(repr(responder))

    def _responder_link_removed(self, controller, responder, group):
        """Remove a responder from the controller/responder list."""
        responder = self._devices[responder]
        if not responder:
            return
        controller_responders = self._controller_responders.get(repr(controller))
        if not controller_responders:
            return
        recs = list(responder.aldb.find(target=controller, group=group))
        if not recs and repr(responder) in controller_responders:
            controller_responders.pop(repr(responder))

    async def _async_check_responders(self, topic=pub.AUTO_TOPIC, **kwargs):
        controller, group, msg_type = _topic_to_addr_group(topic)
        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        if group == 0:
            return

        responders = self._controller_responders.get(controller)
        for responder in responders:
            device = self._devices[responder]
            if device:
                # If the device is a category 1 or 2 device we can pre-load the device state with the
                # ALDB record data1 field value. We will then check the actual status later.
                if device.cat in [0x01, 0x02]:
                    for rec in device.aldb.find(group=group):
                        button = rec.data3 if rec.data3 else 1
                        if button in device.groups:
                            device.groups[button].value = rec.data1
                if not device.is_battery:
                    await device.async_status()

        responders = []
        device_c = self._devices[controller]
        if device_c:
            for mem_addr in device_c.aldb:
                rec = device_c.aldb[mem_addr]
                if (
                    rec.is_in_use
                    and rec.is_controller
                    and rec.group == group
                    and rec.target not in responders
                ):
                    responders.append(rec.target)

        for addr in self._devices:
            if (
                addr == self._devices.modem.address
                or (device_c and addr == device_c.address)
                or addr in responders
            ):
                continue
            device_r = self._devices[addr]
            for mem_addr in device_r.aldb:
                rec = device_r.aldb[mem_addr]
                if (
                    rec.is_in_use
                    and rec.is_responder
                    and rec.target == controller
                    and rec.group == group
                ):
                    responders.append(addr)

        for addr in responders:
            device = self._devices[addr]
            if device:
                await device.async_status()
