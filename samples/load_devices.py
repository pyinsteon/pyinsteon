"""Load saved devices to provide quick startup."""

import asyncio

from pyinsteon import async_close, async_connect
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST  = get_hub_config()


async def do_run():
    """Connect to the PLM and load the ALDB."""
    # devices = await async_connect(device=DEVICE)
    devices = await async_connect(host=HOST,
                                  username=USERNAME,
                                  password=PASSWORD)
    modem = devices.modem
    _LOGGER.info('Connected')
    _LOGGER.info('Modem Address: %s', modem.address)
    await devices.async_load(workdir=PATH)
    await devices.async_save(workdir=PATH)
    for address in devices:
        device = devices[address]
        _LOGGER.info('%s %s %s', device.address, device.description, device.model)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='debug',
                   logger_messages='debug', logger_topics=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
