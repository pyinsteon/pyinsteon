"""Manages links between devices to identify device state of responders."""
import asyncio
import json
import logging
import string
from os import path
from typing import Union

import aiofiles
import voluptuous as vol

from .. import pub
from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..constants import DeviceAction, MessageFlagType
from ..device_types.device_base import Device
from ..device_types.modem_base import ModemBase
from ..topics import ALDB_LINK_CHANGED
from ..utils import subscribe_topic

SCENE_FILE = "insteon_scenes.json"
_LOGGER = logging.getLogger(__name__)
Controller_Address = Address
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


def _json_key_to_int(key):
    """Ensure the Json key is an int."""
    if isinstance(key, dict):
        return {int(k): v for k, v in key.items()}
    return key


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
            Controller_Address,
            dict[Group, dict[ResponderAddress, list[LinkInfo]]],
        ] = {}
        self._scenes: dict[Group, dict[ResponderAddress, list[LinkInfo]]] = {}
        self._scene_names: dict[int, str] = {}
        self._work_dir: Union[str, None] = None
        self._devices.subscribe(self._device_added_or_removed)

    @property
    def scenes(
        self,
    ) -> dict[Group, dict[str, Union[dict[ResponderAddress, LinkInfo], str]]]:
        """Return a list of scenes."""
        return {
            scene_num: self._fill_scene_data(scene=scene, scene_num=scene_num)
            for scene_num, scene in self._scenes.items()
        }

    @property
    def links(
        self,
    ) -> dict[Controller_Address, dict[Group, dict[ResponderAddress, LinkInfo]]]:
        """Return a list of device links."""
        return self._links

    def get_scene(
        self, scene_num: int
    ) -> dict[str, Union[str, dict[ResponderAddress, list[LinkInfo]]]]:
        """Return the device info for a given scene.

        Returns a dictionary:
            name: <scene name>
            devices: dict[ResponderAddress: [LinkInfo]]
        """
        scene_links = self._scenes.get(scene_num)
        if not scene_links:
            return None
        return self._fill_scene_data(scene_links, scene_num)

    def get_responders(
        self, controller: Address, group: int
    ) -> dict[ResponderAddress, LinkInfo]:
        """Return the responders to a controller/group combination."""
        return self._links.get(controller, {}).get(group, {})

    def set_scene_name(self, scene_num: int, name: str):
        """Set the friendly name of a scene."""
        self._scene_names[scene_num] = name

    async def async_load_scene_names(self, work_dir: Union[str, None] = None):
        """Return the scene names."""
        if work_dir is None and self._work_dir is None:
            raise ValueError("No file path has been specified.")
        if work_dir:
            self._work_dir = work_dir
        json_file = {}
        scene_file = path.join(self._work_dir, SCENE_FILE)
        try:
            async with aiofiles.open(scene_file, "r") as afp:
                json_file = await afp.read()
            try:
                saved_devices = json.loads(json_file, object_hook=_json_key_to_int)
                self._scene_names = saved_devices
            except json.decoder.JSONDecodeError:
                _LOGGER.debug("Loading saved device file failed")
        except FileNotFoundError:
            _LOGGER.debug("Saved device file not found")

    async def async_save_scene_names(self, work_dir: Union[str, None] = None):
        """Write the scenes to a file."""
        if self._work_dir is None and work_dir is None:
            raise ValueError("No file path has been specified.")
        if work_dir:
            self._work_dir = work_dir
        out_json = json.dumps(self._scene_names, indent=2)
        scene_file = path.join(self._work_dir, SCENE_FILE)
        async with aiofiles.open(scene_file, "w") as afp:
            await afp.write(out_json)
            await afp.flush()

    async def async_add_device_to_scene(
        self,
        address: Address,
        scene_num: int,
        data1: int = 255,
        data2: int = 0,
        data3: int = 1,
        delay_write: bool = False,
    ):
        """Add a device to a scene."""
        device = self._devices[address]
        modem = self._devices.modem
        device.aldb.add(
            group=scene_num,
            target=modem.address,
            controller=False,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        modem.aldb.add(
            group=scene_num,
            target=device.address,
            controller=True,
            data1=int(device.cat),
            data2=device.subcat,
            data3=device.firmware if device.firmware is not None else 0,
        )
        if not delay_write:
            await device.aldb.async_write()
            await modem.aldb.async_write()

    async def async_remove_device_from_scene(
        self,
        address: Address,
        scene_num: int,
        delay_write: bool = False,
    ):
        """Add a device to a scene."""

        device: Device = self._devices[address]
        modem: ModemBase = self._devices.modem
        for rec in device.aldb.find(
            group=scene_num, target=modem.address, is_controller=False, in_use=True
        ):
            device.aldb.remove(rec.mem_addr)
        for rec in modem.aldb.find(
            group=scene_num, target=device.address, is_controller=True, in_use=True
        ):
            modem.aldb.remove(rec.mem_addr)

        if not delay_write:
            await device.aldb.async_write()
            await modem.aldb.async_write()

    async def async_add_or_update_scene(
        self,
        scene_num: int,
        links: DeviceLinkSchema,
        name: str = None,
    ):
        """Create or update a scene with a list of devices and device link data."""
        try:
            DeviceLinkSchema(links)
        except vol.Error as exc:
            _LOGGER.error("Invalid DeviceLinkSchema format for links parameter.")
            raise exc

        updated_devices = []
        curr_scene = self.get_scene(scene_num)

        if scene_num <= 0:
            scene_num = self._find_next_scene()

        # Remove all records from the current scene
        # Not a big deal since when we add them back they will not need to be writen again if they did not change
        updated_devices = self._remove_scene_links(scene_num, curr_scene)

        # Add the devices from device_info param
        for link in links:
            device = self._devices[link["address"]]
            device.aldb.add(
                group=scene_num,
                target=self._devices.modem.address,
                controller=False,
                data1=link["data1"],
                data2=link["data2"],
                data3=link["data3"],
            )
            if device not in updated_devices:
                updated_devices.append(device)
                self._devices.modem.aldb.add(
                    group=scene_num,
                    target=device.address,
                    controller=True,
                    data1=int(device.cat),
                    data2=device.subcat,
                    data3=device.firmware if device.firmware is not None else 0,
                )

        await self._async_write_scene_link_changes(updated_devices)
        if name:
            self.set_scene_name(scene_num=scene_num, name=name)

    async def async_delete_scene(self, scene_num: int):
        """Delete a scene."""
        curr_scene = self.get_scene(scene_num)
        updated_devices = self._remove_scene_links(scene_num, curr_scene)
        await self._async_write_scene_link_changes(updated_devices)

    def _remove_scene_links(self, scene_num: int, scene_data):
        """Mark all current scene links as unused.

        Does not write to the database.
        """
        updated_devices = []
        if scene_data:
            curr_device_info = scene_data["devices"]
            for addr, info_list in curr_device_info.items():
                device = self._devices[addr]
                for info in info_list:
                    for rec in device.aldb.find(
                        is_controller=False,
                        group=scene_num,
                        target=self._devices.modem.address,
                        data3=info.data3,
                        in_use=True,
                    ):
                        device.aldb.remove(rec.mem_addr)
                        if device not in updated_devices:
                            updated_devices.append(device)
                    for modem_rec in self._devices.modem.aldb.find(
                        is_controller=True,
                        target=device.address,
                        group=scene_num,
                        in_use=True,
                    ):
                        self._devices.modem.aldb.remove(modem_rec.mem_addr)
        return updated_devices

    async def _async_write_scene_link_changes(self, devices):
        """Write the ALDB for the devices changed."""
        for device in devices:
            await device.aldb.async_write()
        await self._devices.modem.aldb.async_write()

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

    def _find_next_scene(self):
        """Return the next available scene number."""
        next_scene = 20
        while next_scene in self.scenes:
            next_scene += 1
        return next_scene

    def _fill_scene_data(
        self, scene: dict[ResponderAddress, list[LinkInfo]], scene_num: int
    ) -> dict[int : dict[string : dict[ResponderAddress, list[LinkInfo]]]]:
        """Fill in the scene name and device info."""
        scene_data = {}
        scene_data["name"] = self._get_scene_name(scene_num)
        scene_data["group"] = scene_num
        scene_data["devices"] = scene
        return scene_data

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

    def _get_scene_name(self, scene_num: int):
        """Return the scene name."""
        return self._scene_names.get(scene_num, f"Insteon scene {scene_num}")

    def _add_link(self, record, controller, responder, has_controller, has_responder):
        """Add a link to the controller/responder list."""
        if self._is_standard_modem_link(controller, responder, record.group):
            return
        # Listen for the controller group topic and check known responders.
        subscribe_topic(self._async_check_responders, f"{controller.id}.{record.group}")

        if self._is_scene_link(controller, responder, record.group):
            self._add_scene(record, responder, has_controller, has_responder)
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

    def _add_scene(self, record, responder, has_controller, has_responder):
        """Add a scene link."""
        scene_num = record.group
        scene = self._scenes.get(scene_num, {})
        if not scene:
            self._scenes[scene_num] = scene
        self._add_link_to_controller_group(
            scene,
            record,
            self._devices.modem.address,
            responder,
            has_controller,
            has_responder,
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
