"""Sample program to demonstrated the loading of the Modem's ALDB."""
import asyncio
from pyinsteon import async_connect, async_close
from samples import set_log_levels, _LOGGER, get_hub_config

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()


async def do_run():
    """Connect to the PLM and load the ALDB."""
    devices = await async_connect(device=DEVICE)
    # modem = await async_connect(host=HOST,
    #                             username=USERNAME,
    #                             password=PASSWORD)
    modem = devices.modem
    _LOGGER.info('Connected')
    _LOGGER.info('Modem Address: %s', modem.address)
    _LOGGER.info('Loading ALDB')
    await modem.aldb.async_load()

    _LOGGER.info('ALDB Load Status: %s', modem.aldb.status)
    for record in modem.aldb:
        _LOGGER.info(modem.aldb[record])
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='debug')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
