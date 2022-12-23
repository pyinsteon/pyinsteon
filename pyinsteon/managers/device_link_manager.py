"""Manages links between devices to identify device state of responders."""
import asyncio
import logging
from typing import Union

import voluptuous as vol

from .. import pub
from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..constants import DeviceAction, MessageFlagType
from ..topics import ALDB_LINK_CHANGED
from ..utils import subscribe_topic

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
        self._links: dict[
            ControllerAddress,
            dict[Group, dict[ResponderAddress, list[LinkInfo]]],
        ] = {}
        self._work_dir: Union[str, None] = None
        self._devices.subscribe(self._device_added_or_removed)

    @property
    def links(
        self,
    ) -> dict[ControllerAddress, dict[Group, dict[ResponderAddress, LinkInfo]]]:
        """Return a list of device links."""
        return self._links

    def get_responders(
        self, controller: Address, group: int
    ) -> dict[ResponderAddress, LinkInfo]:
        """Return the responders to a controller/group combination."""
        return self._links.get(controller, {}).get(group, {})

    def _link_changed(self, record: ALDBRecord, sender: Address, deleted: bool) -> None:
        """Add a record to the controller/responder list."""
        if record.is_controller:
            controller = Address(sender)
            responder = Address(record.target)
            has_controller = True
            has_responder = None
        else:
            controller = Address(record.target)
            responder = Address(sender)
            has_responder = True
            has_controller = None

        if deleted:
            self._remove_link(
                record=record,
                controller=controller,
                responder=responder,
                rem_resp=has_responder,
            )
        else:
            self._add_link(
                record=record,
                controller=controller,
                responder=responder,
                has_controller=has_controller,
                has_responder=has_responder,
            )

    def _get_responder_records(
        self, controller: Address, responder: Address, group: int
    ) -> ALDBRecord:
        """Return the responder's ALDBRecord for the given link."""
        device = self._devices[responder]
        if not device:
            return None
        for rec in device.aldb.find(
            target=controller,
            is_controller=False,
            group=group,
        ):
            yield rec

    def _add_link(self, record, controller, responder, has_controller, has_responder):
        """Add a link to the controller/responder list."""
        if self._is_standard_modem_link(controller, responder, record.group):
            return
        # Listen for the controller group topic and check known responders.
        subscribe_topic(self._async_check_responders, f"{controller.id}.{record.group}")

        if self._is_scene_link(controller, responder, record.group):
            return

        controller_groups = self._links.get(controller, {})
        if not controller_groups:
            self._links[controller] = controller_groups
        controller_group = controller_groups.get(record.group, {})
        if not controller_group:
            controller_groups[record.group] = controller_group

        self._add_link_to_controller_group(
            controller_group,
            record,
            controller,
            responder,
            has_controller,
            has_responder,
        )

    def _add_link_to_controller_group(
        self,
        controller_group,
        record,
        controller,
        responder,
        has_controller,
        has_responder,
    ):
        """Add a link or a scene to a controller group."""
        responder_data: list[LinkInfo] = controller_group.get(responder, [])
        if not responder_data:
            controller_group[responder] = responder_data
        if not responder_data:
            if has_controller:
                # We got a controller record and there are no responder records yet
                responder_data.append(LinkInfo(None, None, None, has_controller, None))
                return

        controller_already_existed = False
        for data in responder_data:
            if has_controller:
                # Update every responder data record with has_controller
                data.has_controller = True
            else:
                if data.data3 == record.data3:
                    # Found a matching record
                    data.has_responder = True
                    return
                elif data.data3 is None:
                    # Found a generic record we can apply this to
                    data.data1 = record.data1
                    data.data2 = record.data2
                    data.data3 = record.data3
                    data.has_responder = True
                    return
                if data.has_controller:
                    controller_already_existed = True
        if has_responder:
            # We did not find a matching record above so add a new responder record
            responder_data.append(
                LinkInfo(
                    record.data1,
                    record.data2,
                    record.data3,
                    controller_already_existed,
                    has_responder,
                )
            )

    def _remove_link(self, record, controller, responder, rem_resp):
        """Remove a controller or responder link from the controller/responder list."""
        group = record.group
        if self._is_standard_modem_link(controller, responder, group):
            return
        controller_groups = self._links.get(controller, {})
        if not controller_groups:
            return
        controller_group = controller_groups.get(group, {})
        if not controller_group:
            return
        responder_data: list[LinkInfo] = controller_group.get(responder, [])
        if not responder_data:
            return
        data_to_remove = []
        if rem_resp:
            for data in responder_data:
                if data.data3 == record.data3:
                    if not data.has_controller:
                        data_to_remove.append(data)
                    else:
                        data.data1 = None
                        data.data2 = None
                        data.data3 = None
                        data.has_responder = False
        else:
            for data in responder_data:
                if not data.has_responder:
                    data_to_remove.append(data)
                else:
                    data.has_controller = False

        for data in data_to_remove:
            self._remove_data_item(controller, group, responder, data)

    def _remove_data_item(self, controller, group, responder, data):
        """Remove a device link data item from the list of controller/responders."""
        controller_group_responders = self._links[controller][group]
        responder_data = controller_group_responders[responder]
        responder_data.remove(data)
        if not responder_data:
            self._links[controller][group].pop(responder)
            if not self._links[controller][group]:
                self._links[controller].pop(group)
                if not self._links[controller]:
                    self._links.pop(controller)

    async def _device_added_or_removed(self, address: Address, action: DeviceAction):
        """Track device list changes."""
        await asyncio.sleep(0.1)
        if action == DeviceAction.REMOVED:
            self._remove_device(address)

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

    def _remove_device(self, address: Address):
        """Remove a device from the controller/responder list."""

        data_to_remove = []
        for controller, controller_group in self._links.items():
            for group, responders in controller_group.items():
                for responder, data_list in responders.items():
                    if not controller == address or not responder == address:
                        continue
                    for data in data_list:
                        if controller == address:
                            if not data.has_responder:
                                data_to_remove.append(
                                    [controller, responder, group, data]
                                )
                            else:
                                data.has_controller = False
                        else:
                            if not data.has_controller:
                                data_to_remove.append(
                                    [controller, responder, group, data]
                                )
                            else:
                                data.has_responder = False
        for data in data_to_remove:
            self._remove_data_item(*data)

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

    def _is_scene_link(self, controller, responder, group):
        """Return if the controller is the modem and the group is not a standard link group."""
        if self._is_standard_modem_link(controller, responder, group):
            return False

        if self._devices.modem and controller == self._devices.modem.address:
            return True

        return False
