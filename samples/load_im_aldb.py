"""Sample program to demonstrated the loading of the Modem's ALDB."""
import asyncio
import logging
import sys
from pyinsteon import async_connect


_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger('pyinsteon')

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
    print('Connected')
    print('Modem Address:', modem.address)
    print('Loading ALDB')
    await modem.aldb.async_load()
    print ('ALDB Load Status: ', modem.aldb.status.name)
    for record in modem.aldb:
        print(modem.aldb[record])
    await modem.async_close()


if __name__ == '__main__':
    stream_handler = logging.StreamHandler(sys.stdout)
    _LOGGER.addHandler(stream_handler)
    _LOGGER_PYINSTEON.addHandler(stream_handler)
    # _LOGGER.setLevel(logging.DEBUG)
    # _LOGGER_PYINSTEON.setLevel(logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
