"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio
import os
import logging
import sys

from pyinsteon import async_connect
from pyinsteon import pub


PATH = os.path.join(os.getcwd(), 'samples')
# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'

DEVICE_ADDRESSES = ['27.C3.87'] # , '45.31.94', '46.2F.24', '13.36.96']

_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger('pyinsteon')


async def load_database():
    """Load the device databae."""
    from pyinsteon import device_mgr
    modem = await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)

    await device_mgr.load_devices(workdir=PATH)
    for address in DEVICE_ADDRESSES:
        device = device_mgr[address]

        _LOGGER.info('Starting DB load for %s', address)
        await device.aldb.async_load()
        _LOGGER.info('ALDB load status: %s', device.aldb.status.name)
        for mem_addr in device.aldb:
            _LOGGER.info(device.aldb[mem_addr])

    await modem.async_close()

def print_topics(topic=pub.AUTO_TOPIC, **kwargs):
    """Print all messages sent."""
    _LOGGER.debug('Topic: %s', topic)
    _LOGGER.debug('kwargs: %s', kwargs)


if __name__ == '__main__':
    stream_handler = logging.StreamHandler(sys.stdout)
    _LOGGER.addHandler(stream_handler)
    _LOGGER_PYINSTEON.addHandler(stream_handler)

    _LOGGER.setLevel(logging.INFO)
    _LOGGER_PYINSTEON.setLevel(logging.INFO)

    # pub.subscribe(print_topics, pub.ALL_TOPICS)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Running database load method')
    loop.run_until_complete(load_database())
