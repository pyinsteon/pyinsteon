"""Manages links between devices to identify device state of responders."""
from .. import pub
from ..address import Address
from ..constants import MessageFlagType
from ..topics import DEVICE_LINK_CONTROLLER_CREATED, DEVICE_LINK_RESPONDER_CREATED
from ..utils import subscribe_topic


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
    """Manages links between devices to identify state of responders.

    Listens for broadcast messages from a device and identifies the responders of the device.
    Once the responders are identified, the state of the responders is determined.
    """

    def __init__(self, devices):
        """Init the DeviceLinkManager class."""
        subscribe_topic(self._controller_link_created, DEVICE_LINK_CONTROLLER_CREATED)
        subscribe_topic(self._controller_link_created, DEVICE_LINK_RESPONDER_CREATED)
        self._devices = devices

    def _controller_link_created(self, controller, responder, group):
        controller_group = _controller_group_topic(controller, group)
        subscribe_topic(self._check_responders, controller_group)

    def _check_responders(self, topic=pub.AUTO_TOPIC, **kwargs):
        controller, group, msg_type = _topic_to_addr_group(topic)
        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        if group == 0:
            return

        responders = []
        device_c = self._devices[controller]
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
                or addr == device_c.address
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
                    # If the device is a category 1 or 2 device we can pre-load the device state with the
                    # ALDB record data1 field value. We will then check the actual status later.
                    if device_r.cat in [0x01, 0x02] and len(device_r.groups) == 1:
                        device_r.groups[1].value = rec.data1

        for addr in responders:
            device = self._devices[addr]
            if device:
                device.status()
