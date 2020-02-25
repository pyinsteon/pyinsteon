"""Load saved devices to provide quick startup."""

import asyncio

from pyinsteon import async_close, async_connect
from pyinsteon.managers.link_manager import async_enter_unlinking_mode
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
    await devices.async_load(workdir=PATH, id_devices=0)
    await async_enter_unlinking_mode(group=1)
    _LOGGER.info('Press device SET button')
    await asyncio.sleep(10)
    await async_enter_unlinking_mode(group=0)
    _LOGGER.info('Press device SET button')
    await asyncio.sleep(10)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='True',
                   logger_messages='debug', logger_topics=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
