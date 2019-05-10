"""Sample program to demonstrate identifing an unknown device.

Any device that is triggered will be identified.
"""
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


async def send_messages():
    """Send the messages to mimic triggering."""
    from binascii import unhexlify
    from pyinsteon import devices
    address = '27c387'
    RX1 = unhexlify('0250{}000001cf1300'.format(address))
    #pylint: disable=protected-access
    devices.modem._protocol.data_received(RX1)


async def load_database():
    """Load the device databae."""
    from pyinsteon import devices
    await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)

    await devices.async_load(workdir=PATH, id_devices=0)
    _LOGGER.info('Trigger the device now...')
    # Uncomment the line below to mock a device sending a message.
    # asyncio.ensure_future(send_messages())
    await asyncio.sleep(10)
    for address in devices:
        device = devices[address]
        _LOGGER.info('Device: %s %s', device.address, device.description)
    await async_close()


if __name__ == '__main__':
    stream_handler = logging.StreamHandler(sys.stdout)
    _LOGGER.addHandler(stream_handler)
    _LOGGER_PYINSTEON.addHandler(stream_handler)

    _LOGGER.setLevel(logging.INFO)
    _LOGGER_PYINSTEON.setLevel(logging.INFO)
    _LOGGER_MSG.setLevel(logging.DEBUG)

    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(load_database())
