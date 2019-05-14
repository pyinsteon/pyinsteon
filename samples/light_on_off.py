"""Load saved devices to provide quick startup."""

import asyncio
from pyinsteon import async_connect, devices, async_close
from . import _LOGGER, set_log_levels, PATH


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
HOST = '192.168.1.136'
USERNAME = 'username'
PASSWORD = 'password'


def state_changed(name, value, group):
    """Capture the state change."""
    _LOGGER.info('State changed to %s', value)


async def do_run():
    """Connect to the PLM and load the ALDB."""
    modem = await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)
    _LOGGER.info('Connected')
    _LOGGER.info('Modem Address: %s', modem.address)
    await devices.async_load(workdir=PATH, id_devices=0)
    device = devices['27.C3.87']
    device.states[0].subscribe(state_changed)
    await device.async_on()
    await asyncio.sleep(1)
    await device.async_off()

    _LOGGER.info('Please manually turn device on and off.')
    await asyncio.sleep(20)

    _LOGGER.info('Getting device status.')
    await device.async_status()
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='info')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
