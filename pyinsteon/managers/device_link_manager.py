"""Manages links between devices to identify device state of responders."""
from .. import pub
from ..address import Address
from ..constants import MessageFlagType
from ..topics import (
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from ..utils import subscribe_topic


def _controller_group_topic(controller, group):
    return f"{controller.id}.{group}"


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

    def __init__(self, devices):
        """Init the DeviceLinkManager class."""
        subscribe_topic(self._controller_link_created, DEVICE_LINK_CONTROLLER_CREATED)
        subscribe_topic(self._controller_link_created, DEVICE_LINK_RESPONDER_CREATED)
        subscribe_topic(self._controller_link_created, DEVICE_LINK_RESPONDER_REMOVED)
        self._devices = devices
        self._controller_responders = {}

    def _controller_link_created(self, controller, responder, group):
        # If the modem is a responder we don't need to worry about tracking that
        if responder == self._devices.modem.address:
            return
        controller_group = _controller_group_topic(controller, group)
        subscribe_topic(self._async_check_responders, controller_group)

        if not self._controller_responders.get(controller):
            self._controller_responders[controller] = {}
        if not self._controller_responders[controller].get(group):
            self._controller_responders[controller][group] = []
        if responder not in self._controller_responders[controller][group]:
            self._controller_responders[controller][group].append(responder)

    async def _async_check_responders(self, topic=pub.AUTO_TOPIC, **kwargs):
        controller, group, msg_type = _topic_to_addr_group(topic)

        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        if group == 0:
            return
        known_responders = self._controller_responders.get(controller, {}).get(
            group, {}
        )

        # Check known responers for current status
        for responder in known_responders:
            resp_device = self._devices[responder]
            # If the device is a category 1 or 2 device we can pre-load the device state with the
            # ALDB record data1 field value. We will then check the actual status later.
            if resp_device and resp_device.cat in [0x01, 0x02]:
                for rec in resp_device.aldb.find(
                    target=controller, group=group, is_controller=False
                ):
                    resp_device.groups[group].value = rec.data1
            await resp_device.async_status()

        # See if the controller knows about other responders
        if device_c := self._devices[controller]:
            for rec in device_c.aldb.find(group=group, is_controller=True):
                if (
                    rec.target not in known_responders
                    and rec.target != self._devices.modem.address
                ):
                    known_responders.append(rec.target)
                    if device_r := self._devices[rec.target]:
                        await device_r.async_status()

        # Check the rest of the devices if they are a responder
        for addr in self._devices:
            if addr == self._devices.modem.address:
                continue
            if addr in known_responders:
                continue
            device_r = self._devices[addr]
            for rec in resp_device.aldb.find(
                target=controller, group=group, is_controller=False
            ):
                await device_r.async_status()
                break
