"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_connect, devices, async_close
from samples import set_log_levels, _LOGGER, PATH


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'


async def load_database():
    """Load the device databae."""
    await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)

    await devices.async_load(workdir=PATH)
    await devices.async_save(workdir=PATH)
    for address in devices:
        device = devices[address]
        if not device.aldb.is_loaded:
            _LOGGER.info('\nStarting DB load for %s', address)
            await device.aldb.async_load()
            await devices.async_save(workdir=PATH)
        _LOGGER.info('\nALDB load status for %s: %s', device.address, device.aldb.status.name)
        for mem_addr in device.aldb:
            _LOGGER.info(device.aldb[mem_addr])
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='debug')
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(load_database())
