"""Load saved devices to provide quick startup."""

import asyncio

from pyinsteon import async_close, async_connect
from pyinsteon.managers.link_manager import async_unlink_devices
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()


def state_changed(name, value, group):
    """Capture the state change."""
    _LOGGER.info('State changed to %s', value)


async def do_run():
    """Connect to the PLM and load the ALDB."""
    devices = await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)
    modem = devices.modem
    _LOGGER.info('Connected')
    _LOGGER.info('Modem Address: %s', modem.address)
    await devices.async_load(workdir=PATH, id_devices=0)
    controller = devices.get('45.31.94')
    responder = devices.get('13.36.96')
    await controller.aldb.async_load(refresh=True)
    await responder.aldb.async_load(refresh=True)
    link_result = await async_unlink_devices(controller, responder, 1)
    if link_result:
        _LOGGER.info(link_result)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='debug', logger_pyinsteon='info', logger_messages='info', logger_topics=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
