"""Manage Insteon Scenes."""
import asyncio
import logging

from .. import devices
from ..device_types.plm import PLM
from ..handlers.send_all_link_off import SendAllLinkOffCommandHandler
from ..handlers.send_all_link_on import SendAllLinkOnCommandHandler
from .link_manager import async_link_devices

_LOGGER = logging.getLogger(__name__)


class Scenes:
    """Manage a list of scenes."""

    def __init__(self):
        """Init the Scenes class."""
        self._scenes = {}

    def __setitem__(self, group, device):
        """Add a device to a scene."""
        device_list = self._scenes.get(group, [])
        if device not in device_list:
            device_list.append(device)
            self._scenes[group] = device_list

    def __getitem__(self, group):
        """Get a list of links associated with a scene."""
        return self._scenes.get(group, [])

    def get_devices(self, group):
        """Return the devices associated with a scene (group controller tuple)."""
        scene = self._scenes.get(group)
        if scene:
            for device in scene:
                if device:
                    yield device


def identify_scenes():
    """Look through device All-Link databases and find scenes."""
    modem = devices.modem
    scenes = Scenes()
    for address in devices:
        device = devices[address]
        for mem_addr in device.aldb:
            rec = device.aldb[mem_addr]
            if (
                rec.group != 0
                and rec.is_responder
                and rec.target == modem.address
                and rec.is_in_use
            ):
                scenes[rec.group] = device
    for mem_addr in modem.aldb:
        rec = modem.aldb[mem_addr]
        if rec.is_controller and rec.group != 0:
            scenes[rec.group] = devices[rec.target]
    return scenes


async def async_add_device_to_scene(
    device, group: int, on_level=0xFF, ramp_rate=0x28, button=0
):
    """Create a new scene.

    Parameters:
    - group: Scene number.
    - device_scene_info: Iterable colleciton of SceneInfo objects.

    """
    if isinstance(devices.modem, PLM):
        await _plm_add_device_to_scene(group, device, on_level, ramp_rate, button)
    else:
        pass


async def async_trigger_scene_on(group):
    """Trigger an Insteon scene."""
    scenes = identify_scenes()

    await SendAllLinkOnCommandHandler().async_send(group=group)

    await asyncio.sleep(2)
    for device in scenes.get_devices(group):
        await device.async_status()


async def async_trigger_scene_off(group):
    """Trigger an Insteon scene."""
    scenes = identify_scenes()

    await SendAllLinkOffCommandHandler().async_send(group=group)

    await asyncio.sleep(2)
    for device in scenes.get_devices(group):
        await device.async_status()


async def _plm_add_device_to_scene(group, device, on_level, ramp_rate, button):
    modem = devices.modem
    device.aldb.add(
        group=group,
        target=modem.address,
        controller=False,
        data1=on_level,
        data2=ramp_rate,
        data3=button,
    )
    modem.aldb.add(
        group=group, target=device.address, controller=True, data1=0, data2=0, data3=0
    )
    # TODO check for success or failure
    await device.aldb.async_write()
    await modem.aldb.async_write()


async def _hub_add_device_to_scene(group, device, on_level, ramp_rate, button):
    # TODO check for success or failure
    await device.async_status()
    curr_state = device.groups[group].value
    await _set_device_state(device, on_level, button)
    await async_link_devices(devices.modem, device, group)
    await _set_device_state(device, curr_state, button)


async def _set_device_state(device, on_level, button):
    if device.cat == 0x01:
        device.on(on_level=on_level, group=button)
    elif device.cat == 0x02:
        if on_level:
            device.on(group=button)
        else:
            device.off(group=button)
