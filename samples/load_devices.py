"""Load saved devices to provide quick startup."""

import asyncio
from pyinsteon import async_connect, devices, async_close
from . import set_log_levels, _LOGGER, PATH


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'


async def do_run():
    """Connect to the PLM and load the ALDB."""
    modem = await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)
    _LOGGER.info('Connected')
    _LOGGER.info('Modem Address: %s', modem.address)
    await devices.async_load(workdir=PATH)
    # await devices.save_devices(workdir=PATH)
    for address in devices:
        device = devices[address]
        _LOGGER.info(device.address, device.description, device.model)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='info')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
