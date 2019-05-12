"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio
import os
import logging
import sys

from pyinsteon import async_connect, async_close


PATH = os.path.join(os.getcwd(), 'samples')
# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'

_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger('pyinsteon')
_LOGGER_MSG = logging.getLogger('pyinsteon.messages')


async def load_database():
    """Load the device databae."""
    from pyinsteon import devices
    await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)

    await devices.async_load(workdir=PATH)
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
    stream_handler = logging.StreamHandler(sys.stdout)
    _LOGGER.addHandler(stream_handler)
    _LOGGER_PYINSTEON.addHandler(stream_handler)

    _LOGGER.setLevel(logging.INFO)
    _LOGGER_PYINSTEON.setLevel(logging.INFO)
    _LOGGER_MSG.setLevel(logging.INFO)

    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(load_database())
