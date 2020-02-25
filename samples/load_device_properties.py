"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_close, async_connect
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()


async def load_device_properties():
    """Load the device databae."""
    # devices = await async_connect(device=DEVICE)
    devices = await async_connect(host=HOST,
                                  username=USERNAME,
                                  password=PASSWORD)

    await devices.async_load(workdir=PATH)
    await devices.async_save(workdir=PATH)
    for address in devices:
        device = devices[address]
        _LOGGER.info('Loading device properties')
        await device.async_read_config()

        await devices.async_save(workdir=PATH)
        _LOGGER.info('')
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='debug', logger_topics=True)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(load_device_properties())
