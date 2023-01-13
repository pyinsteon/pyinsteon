"""Manages links between devices to identify device state of responders."""
import asyncio
import logging
from typing import Dict, Union

import voluptuous as vol

from .. import pub
from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..constants import AllLinkMode, DeviceAction, MessageFlagType
from ..topics import ALDB_LINK_CHANGED
from ..utils import subscribe_topic, unsubscribe_topic

_LOGGER = logging.getLogger(__name__)
ControllerAddress = Address
ResponderAddress = Address
Group = int

DeviceLinkSchema = vol.Schema(
    [
        {
            vol.Required("address"): str,
            vol.Required("data1"): int,
            vol.Required("data2"): int,
            vol.Required("data3"): int,
        }
    ]
)


class LinkInfo:
    """Device link data class."""

    def __init__(self, data1, data2, data3, has_controller, has_responder):
        """Init the LinkInfo class."""
        self.data1 = data1
        self.data2 = data2
        self.data3 = data3
        self.has_controller = has_controller
        self.has_responder = has_responder


EMPTY_ADDRESS = Address("000000")


def _add_controller_group_responder_tree(links, controller, group, responder):
    """Add a controller, group, responder set."""
    if not links.get(controller):
        links[controller] = {}
    if not links[controller].get(group):
        links[controller][group] = {}
    if not links[controller][group].get(responder):
        links[controller][group][responder] = []
    return links


def _add_controller_link(links, controller, record):
    """Add a controller link."""
    return _add_controller_group_responder_tree(
        links, controller, record.group, record.target
    )


def _add_responder_link(links, devices, responder, record):
    """Add a responder link."""
    links = _add_controller_group_responder_tree(
        links, record.target, record.group, responder
    )
    responder_links = links[record.target][record.group][responder]
    controller_device = devices[record.target]
    has_controller = False
    if controller_device:
        for _ in controller_device.aldb.find(
            target=responder,
            is_controller=True,
            group=record.group,
        ):
            has_controller = True
    link = LinkInfo(record.data1, record.data2, record.data3, has_controller, True)
    responder_links.append(link)
    return links


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
        self._devices = devices
        self._work_dir: Union[str, None] = None
        self._devices.subscribe(self._device_added_or_removed)

    @property
    def links(
        self,
    ) -> Dict[ControllerAddress, Dict[Group, Dict[ResponderAddress, LinkInfo]]]:
        """Return a list of device links."""
        return self._get_links()

    def get_responders(
        self, controller: Address, group: int
    ) -> Dict[ResponderAddress, LinkInfo]:
        """Return the responders to a controller/group combination."""
        responders = self._get_links(controller, group)
        return responders.get(controller, {}).get(group, {})

    def _get_links(self, controller=None, group=None):
        """Return a list of links.

        If controller is not None -> Only return responders for that controller
        If group is not None -> Only return responders for that group
        """
        modem_address = self._devices.modem.address if self._devices.modem else None
        links = {}
        for addr in self._devices:
            if addr == modem_address:
                continue
            device = self._devices[addr]
            for mem_addr in device.aldb:
                rec: ALDBRecord = device.aldb[mem_addr]
                if (
                    rec.target == modem_address
                    or rec.target == EMPTY_ADDRESS
                    or not rec.is_in_use
                ):
                    continue
                if rec.mode == AllLinkMode.CONTROLLER:
                    if not controller or device.address == controller:
                        links = _add_controller_link(links, device.address, rec)
                    continue
                if (not controller or rec.target == controller) and (
                    not group or rec.group != group
                ):
                    links = _add_responder_link(
                        links, self._devices, device.address, rec
                    )
        return links

    def _link_changed(self, record: ALDBRecord, sender: Address, deleted: bool) -> None:
        """Add a record to the controller/responder list."""
        if record.is_controller:
            controller = Address(sender)
            responder = Address(record.target)
        else:
            controller = Address(record.target)
            responder = Address(sender)

        if deleted:
            self._remove_link(record=record, controller=controller)
        else:
            self._add_link(record=record, controller=controller, responder=responder)

    def _add_link(self, record, controller, responder):
        """Add a link to the controller/responder list."""
        if self._is_standard_modem_link(controller, responder, record.group):
            return
        # Listen for the controller group topic and check known responders.
        subscribe_topic(self._async_check_responders, f"{controller.id}.{record.group}")

    def _remove_link(self, record, controller):
        """Remove a controller or responder link from the controller/responder list."""
        responders = self.get_responders(controller, record.group)
        if not responders:
            unsubscribe_topic(
                self._async_check_responders, f"{controller.id}.{record.group}"
            )

    async def _device_added_or_removed(self, address: Address, action: DeviceAction):
        """Track device list changes."""
        await asyncio.sleep(0.1)
        if action == DeviceAction.REMOVED:
            unsubscribe_topic(self._link_changed, f"{address.id}.{ALDB_LINK_CHANGED}")

        elif action == DeviceAction.ADDED:
            device = self._devices[address]
            if not device:
                await asyncio.sleep(0.1)
                device = self._devices[address]
                if not device:
                    subscribe_topic(
                        self._link_changed, f"{address.id}.{ALDB_LINK_CHANGED}"
                    )
                    return
            device.aldb.subscribe_record_changed(self._link_changed)
            for _, record in device.aldb.items():
                if record.is_in_use:
                    self._link_changed(record=record, sender=address, deleted=False)

    async def _async_check_responders(self, topic=pub.AUTO_TOPIC, **kwargs) -> None:
        controller, group, msg_type = _topic_to_addr_group(topic)

        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        if group == 0:
            return
        responder_data = self.get_responders(controller, group)
        for addr, data_list in responder_data.items():
            device = self._devices[addr]
            if device:
                # If the device is a category 1 or 2 device we can pre-load the device state with the
                # ALDB record data1 field value. We will then check the actual status later.
                for data in data_list:
                    if device.cat in [0x01, 0x02] and data.data3 is not None:
                        device.groups[data.data3].value = data.data1
                if not device.is_battery:
                    await device.async_status()

    def _is_standard_modem_link(self, controller, responder, group):
        """Test if a link is a standard modem link."""
        if self._devices.modem and responder == self._devices.modem.address:
            return True
        if self._devices.modem and controller == self._devices.modem.address:
            device = self._devices[responder]
            if device:
                groups = list(device.groups)
            groups.append(0)
            if group in groups:
                return True
        return False
