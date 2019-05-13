"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_connect, devices, async_close
from . import set_log_levels, _LOGGER, PATH


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'
DEVICE_ADDRESS = '27.C3.87'


async def write_database():
    """Load the device databae."""
    await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)

    await devices.async_load(workdir=PATH, id_devices=0)
    device = devices[DEVICE_ADDRESS]

    if not device.aldb.is_loaded:
        _LOGGER.info('Starting DB load for %s', DEVICE_ADDRESS)
        await device.aldb.async_load()
        _LOGGER.info('ALDB load status: %s', device.aldb.status.name)
        for mem_addr in device.aldb:
            _LOGGER.info(device.aldb[mem_addr])

    device.aldb.remove(mem_addr=0x0faf)
    _LOGGER.info('Modifing record: %s', '0x0faf')
    await device.aldb.async_write_records()
    for mem_addr in device.aldb:
        _LOGGER.info(device.aldb[mem_addr])
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='info')
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(write_database())
