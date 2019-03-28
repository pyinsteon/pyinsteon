"""Sample program to demonstrated the loading of the Modem's ALDB."""
import asyncio
import logging
import sys
from pyinsteon.devices.modem import PLM


_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger('pyinsteon.aldb')



async def do_run():
    """Connect to the PLM and load the ALDB."""
    plm = PLM('COM5')
    await plm.async_connect()
    print('Connected')
    print('Loading ALDB')
    await plm.aldb.async_load()
    print ('ALDB Load Status: ', plm.aldb.status.name)
    for record in plm.aldb:
        print(plm.aldb[record])
    await plm.async_close()


if __name__ == '__main__':
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER_PYINSTEON.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    _LOGGER.addHandler(stream_handler)
    _LOGGER_PYINSTEON.addHandler(stream_handler)
    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER_PYINSTEON.setLevel(logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
