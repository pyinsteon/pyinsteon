"""Manages links between devices to identify device state of responders."""
import json
import logging
from collections import namedtuple
from os import path

import aiofiles
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

SCENE_FILE = "insteon_scenes.json"
_LOGGER = logging.getLogger(__name__)
DeviceLinkData = namedtuple("DeviceLinkData", "cat data1 data2 data3")


def _jsonKeyToInt(x):
    """Ensure the Json key is an int."""
    if isinstance(x, dict):
        return {int(k): v for k, v in x.items()}
    return x


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

    def __init__(self, devices, work_dir: str | None = None):
        """Init the DeviceLinkManager class."""
        subscribe_topic(self._responder_link_created, DEVICE_LINK_CONTROLLER_CREATED)
        subscribe_topic(self._responder_link_created, DEVICE_LINK_RESPONDER_CREATED)
        subscribe_topic(self._responder_link_removed, DEVICE_LINK_RESPONDER_REMOVED)
        self._devices = devices
        # Dict of {address: {group: [address]}}
        self._controller_responders: dict[Address, dict[int, list[Address]]] = {}
        self._scene_names: dict[int, str] = {}
        self._work_dir: str | None = work_dir

    @property
    def scenes(self) -> dict[int, dict[str, dict[Address, DeviceLinkData] | str]]:
        """Return a list of scenes."""
        if not self._devices.modem:
            return {}
        if not self._scene_names:
            self._load_scenes_from_file()
        scenes = self._get_device_link_data(self._devices.modem.address)
        return self._fill_scene_data(scenes)

    @property
    def links(self) -> dict[Address, dict[int, dict[Address, DeviceLinkData]]]:
        """Return a list of device links."""
        if not self._devices.modem:
            return {
                controller: self._get_device_link_data(controller)
                for controller in self._controller_responders
            }
        return {
            controller: self._get_device_link_data(controller)
            for controller in self._controller_responders
            if controller != self._devices.modem.address
        }

    def get_scene(self, group) -> dict[str, str | dict[Address, DeviceLinkData]]:
        """Return the device info for a given scene."""
        if not self._devices.modem:
            return {}
        if not self._scene_names:
            self._load_scenes_from_file()
        scene = self._get_device_link_data(self._devices.modem.address, group)
        return self._fill_scene_data(scene).get(group)

    def get_link(self, controller: Address, group: int):
        """Return the links to a controller/group combination."""
        return self._get_device_link_data(Address(controller), group).get(group)

    def set_scene_name(self, scene: int, name: str):
        """Set the friendly name of a scene."""
        self._scene_names[scene] = name

    async def async_load_scene_names(self, work_dir: str | None = None):
        """Return the scene names."""
        if work_dir is None and self._work_dir is None:
            raise ValueError("No file path has been specified.")
        if work_dir:
            self._work_dir = work_dir
        return await self._load_scenes_from_file()

    async def async_save_scene_names(self, work_dir: str | None = None):
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

    async def _load_scenes_from_file(self, work_dir: str | None = None):
        """Convert a collection of scenes to json."""
        if self._work_dir is None and work_dir is None:
            raise ValueError("No file path has been specified.")
        if work_dir:
            self._work_dir = work_dir
        json_file = {}
        scene_file = path.join(self._work_dir, SCENE_FILE)
        try:
            async with aiofiles.open(scene_file, "r") as afp:
                json_file = await afp.read()
            try:
                saved_devices = json.loads(json_file, object_hook=_jsonKeyToInt)
                self._scene_names = saved_devices
            except json.decoder.JSONDecodeError:
                _LOGGER.debug("Loading saved device file failed")
        except FileNotFoundError:
            _LOGGER.debug("Saved device file not found")

    def _fill_scene_data(self, scenes):
        """Fill in the scene name and device info."""
        if not self._scene_names and self._work_dir is not None:
            self._load_scenes_from_file(self._work_dir)
        scenes_data = {}
        for scene_num, scene_info in scenes.items():
            scenes_data[scene_num] = {}
            scenes_data[scene_num]["name"] = self._scene_names.get(
                scene_num, f"Insteon scene {scene_num}"
            )
            scenes_data[scene_num]["devices"] = scene_info
        return scenes_data

    def _get_device_link_data(
        self, controller: Address, group: int | None = None
    ) -> dict[int, dict[Address, DeviceLinkData]]:
        """Return the device data 1 - 3 for the given links."""

        if group is None:
            links = self._controller_responders[controller]
        else:
            links = {}
            links[group] = self._controller_responders[controller][group]
        links_data = {}
        for group, addrs in links.items():
            links_data[group] = {}
            for addr in addrs:
                link_info = DeviceLinkData(None, None, None, None)
                device = self._devices[addr]
                if device:
                    for rec in device.aldb.find(
                        target=controller,
                        is_controller=False,
                        group=group,
                    ):
                        link_info = DeviceLinkData(
                            device.cat, rec.data1, rec.data2, rec.data3
                        )
                links_data[group][addr] = link_info
        return links_data

    def _responder_link_created(self, controller, responder, group) -> None:
        controller = Address(controller)
        responder = Address(responder)
        if (
            self._devices.modem and responder == self._devices.modem.address
        ) or group == 0:
            return
        topic = _controller_group_topic(controller, group)
        subscribe_topic(self._async_check_responders, topic.name)
        controller_groups = self._controller_responders.get(controller, {})
        controller_group = controller_groups.get(group, [])
        if responder not in controller_group:
            controller_group.append(responder)
        controller_groups[group] = controller_group
        self._controller_responders[controller] = controller_groups

    def _responder_link_removed(self, controller, responder, group) -> None:
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

    async def _async_check_responders(self, topic=pub.AUTO_TOPIC, **kwargs) -> None:
        controller, group, msg_type = _topic_to_addr_group(topic)

        if msg_type != MessageFlagType.ALL_LINK_BROADCAST:
            return
        if group == 0:
            return
        responder_data = self._get_device_link_data(controller, group).get(group, {})

        for addr, link_data in responder_data.items():
            if link_data.cat is not None:
                device = self._devices[addr]
                # If the device is a category 1 or 2 device we can pre-load the device state with the
                # ALDB record data1 field value. We will then check the actual status later.
                if link_data.cat in [0x01, 0x02]:
                    device.groups[link_data.data3].value = link_data.data1
                if not device.is_battery:
                    await device.async_status()
