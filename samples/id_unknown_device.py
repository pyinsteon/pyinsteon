"""Sample program to demonstrate identifing an unknown device.

Any device that is triggered will be identified.
"""
import asyncio

from pyinsteon import async_connect, devices, async_close
from . import _LOGGER, set_log_levels, PATH


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'

async def send_messages():
    """Send the messages to mimic triggering."""
    from binascii import unhexlify

    address = '27c387'
    RX1 = unhexlify('0250{}000001cf1300'.format(address))
    #pylint: disable=protected-access
    devices.modem._protocol.data_received(RX1)


async def load_database():
    """Load the device databae."""
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
    set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='info')
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(load_database())
