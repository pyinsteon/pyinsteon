"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_connect, async_close
from samples import set_log_levels, _LOGGER, PATH, get_hub_config

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()


async def load_device_properties():
    """Load the device databae."""
    # devices = await async_connect(device=DEVICE)
    devices = await async_connect(host=HOST,
                                  username=USERNAME,
                                  password=PASSWORD)

    await devices.async_load(workdir=PATH, id_devices=2)
    await devices.async_save(workdir=PATH)
    for address in devices:
        device = devices[address]
        if not device.aldb.is_loaded:
            _LOGGER.info('Starting DB load for %s', address)
            await device.aldb.async_load()
        _LOGGER.info('ALDB load status for %s: %s', device.address, device.aldb.status.name)
        _LOGGER.info('Loading device properties')
        await device.async_get_operating_flags()
        await device.async_get_extended_properties()
        await asyncio.sleep(3) # Give the device some time to respond to get ext prop

        await devices.async_save(workdir=PATH)
        _LOGGER.info('')
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=False)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(load_device_properties())
