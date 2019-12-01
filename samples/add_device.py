"""Load saved devices to provide quick startup."""

import asyncio
from pyinsteon import async_connect, async_close
from pyinsteon.managers.link_manager import (
    async_enter_linking_mode, async_create_default_links)
from samples import set_log_levels, _LOGGER, PATH, get_hub_config


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST  = get_hub_config()

async def async_setup_device(address):
    from pyinsteon import devices
    device = devices[address]
    await async_create_default_links(device)
    await device.aldb.async_load(refresh=True)
    await device.async_get_operating_flags()
    await device.async_get_extended_properties()
    await asyncio.sleep(3)
    await devices.async_save(workdir=PATH)

def device_added(address):
    asyncio.ensure_future(async_setup_device(address))

async def do_run():
    """Connect to the PLM and load the ALDB."""
    # devices = await async_connect(device=DEVICE)
    devices = await async_connect(host=HOST,
                                  username=USERNAME,
                                  password=PASSWORD)
    await devices.async_load(workdir=PATH, id_devices=0)
    devices.subscribe(device_added)
    await async_enter_linking_mode(is_controller=True, group=0)
    _LOGGER.info('Press device SET button')
    await asyncio.sleep(60)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='True',
                   logger_messages='debug', logger_topics=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
