"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_connect, devices, async_close
from samples import set_log_levels, _LOGGER, PATH, get_hub_config

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()


async def load_device_properties():
    """Load the device databae."""
    await async_connect(device=DEVICE)
    # await async_connect(host=HOST,
    #                     username=USERNAME,
    #                     password=PASSWORD)

    await devices.async_load(workdir=PATH)
    await devices.async_save(workdir=PATH)
    for address in devices:
        device = devices[address]
        if not device.aldb.is_loaded:
            _LOGGER.info('\nStarting DB load for %s', address)
            await device.aldb.async_load()
            await devices.async_save(workdir=PATH)
        _LOGGER.info('\nALDB load status for %s: %s', device.address, device.aldb.status.name)
        await device.async_get_operating_flags()
        await device.async_get_extended_properties()
        for mem_addr in device.aldb:
            _LOGGER.info(device.aldb[mem_addr])
        for flag in device.operating_flags:
            _LOGGER.info('%s: %s', flag, device.operating_flags[flag])
        for flag in device.ext_properties:
            _LOGGER.info('%s: %s', flag, device.ext_properties[flag])
        await devices.async_save(workdir=PATH)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=False)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(load_device_properties())
