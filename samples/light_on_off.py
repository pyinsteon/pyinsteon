"""Load saved devices to provide quick startup."""

import asyncio
import logging
import os
import sys
from pyinsteon import async_connect, devices


_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger('pyinsteon')

PATH = os.path.join(os.getcwd(), 'samples')
# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'


def state_changed(name, value, group):
    print('State changed to', value)


async def do_run():
    """Connect to the PLM and load the ALDB."""
    modem = await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)
    print('Connected')
    print('Modem Address:', modem.address)
    await devices.load_devices(workdir=PATH, id_devices=0)
    device = devices['27.C3.87']
    device.states[0].subscribe(state_changed)
    await device.async_on()
    await asyncio.sleep(1)
    await device.async_off()
    print('Please manually turn device on and off.')
    await asyncio.sleep(20)
    print('Getting device status.')
    await device.async_status()
    await modem.async_close()


if __name__ == '__main__':
    stream_handler = logging.StreamHandler(sys.stdout)
    _LOGGER.addHandler(stream_handler)
    _LOGGER_PYINSTEON.addHandler(stream_handler)
    # _LOGGER.setLevel(logging.DEBUG)
    # _LOGGER_PYINSTEON.setLevel(logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
