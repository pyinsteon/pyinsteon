"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_connect, devices, async_close
from pyinsteon.managers.link_manager import async_create_default_links
from samples import set_log_levels, _LOGGER, PATH, get_hub_config

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()
address = '27.C3.87'


async def set_default_links():
    """Load the device databae."""
    await async_connect(device=DEVICE)
    # await async_connect(host=HOST,
    #                     username=USERNAME,
    #                     password=PASSWORD)

    await devices.async_load(workdir=PATH, id_devices=0)

    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=True)

    await async_create_default_links(devices[address])

    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=False)
    await devices.modem.aldb.async_load()
    await devices[address].aldb.async_load(refresh=True)

    _LOGGER.info('\nModem Links')
    for mem_addr in devices.modem.aldb:
        _LOGGER.info(devices.modem.aldb[mem_addr])

    _LOGGER.info('\nDevice Links')
    for mem_addr in devices[address].aldb:
        _LOGGER.info(devices[address].aldb[mem_addr])
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=False)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(set_default_links())
