"""Manage Insteon Scenes."""
import asyncio

from .. import devices
from ..handlers.send_all_link_off import SendAllLinkOffCommandHandler
from ..handlers.send_all_link_on import SendAllLinkOnCommandHandler


async def _get_scene_device_status(group: int):
    """Get the status of the devices in a scene."""
    scene = devices.link_manager.get_scene(group)
    for addr in scene:
        device = devices[addr]
        await device.async_status()


async def async_trigger_scene_on(group):
    """Trigger an Insteon scene ON."""
    await SendAllLinkOnCommandHandler().async_send(group=group)
    await asyncio.sleep(2)
    await _get_scene_device_status(group)


async def async_trigger_scene_off(group):
    """Trigger an Insteon scene OFF."""
    await SendAllLinkOffCommandHandler().async_send(group=group)
    await asyncio.sleep(2)
    await _get_scene_device_status(group)
