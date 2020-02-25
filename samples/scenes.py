"""Test creating and triggering a scene."""

import asyncio

from pyinsteon import async_close, async_connect
from pyinsteon.managers.scene_manager import (async_trigger_scene_off,
                                              async_trigger_scene_on,
                                              identify_scenes)
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = "COM5"
USERNAME, PASSWORD, HOST = get_hub_config()


def state_changed(name, address, value, group):
    """Capture the state change."""
    _LOGGER.info("Device %s state %d changed to 0x%02x", address, group, value)


async def do_run():
    """Connect to the PLM and load the ALDB."""
    # devices = await async_connect(device=DEVICE)
    devices = await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    await devices.async_load(workdir=PATH, id_devices=0)
    # modem = devices.modem '', '13.37.42'
    identify_scenes()
    device1 = devices["2C.38.32"]
    device1.groups[1].subscribe(state_changed)
    device2 = devices["13.37.42"]
    device2.groups[1].subscribe(state_changed)
    _LOGGER.info("Turning scene on")
    await async_trigger_scene_on(group=0x1A)
    await asyncio.sleep(5)
    _LOGGER.info("Turning scene off")
    set_log_levels(
        logger="info",
        logger_pyinsteon="info",
        logger_messages="info",
        logger_topics=False,
    )
    await async_trigger_scene_off(group=0x1A)
    await asyncio.sleep(5)
    await async_close()


if __name__ == "__main__":
    set_log_levels(
        logger="info",
        logger_pyinsteon="info",
        logger_messages="info",
        logger_topics=False,
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
