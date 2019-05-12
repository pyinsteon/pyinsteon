"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio
import logging
import os
import sys

from pyinsteon import pub

from pyinsteon import async_connect

PATH = os.path.join(os.getcwd(), 'samples')
# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'

DEVICE_ADDRESS = '27.C3.87'

_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger('pyinsteon')
_LOGGER_MSG = logging.getLogger('pyinsteon.messages')


async def write_database():
    """Load the device databae."""
    from pyinsteon import devices
    modem = await async_connect(device=DEVICE)
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
    _LOGGER_MSG.setLevel(logging.DEBUG)

    # pub.subscribe(print_topics, pub.ALL_TOPICS)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(write_database())
