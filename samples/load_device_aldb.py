"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio
import logging
import os
import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from pyinsteon.devices import Device
from pyinsteon.devices.modem import PLM
from pyinsteon import pub

PORT = '/dev/ttyS5'
# PORT = 'COM5'
DEVICE_ADDRESSES = ['27.C3.87', '45.31.94', '46.2F.24', '13.36.96']
DEVICE_CAT = 0x02
DEVICE_SUBCAT = 0x00
DEVICE_DESCRIPTION = 'Generic on/off device'

_LOGGER = logging.getLogger(__name__)
_LOGGER_PYINSTEON = logging.getLogger('pyinsteon')


class TestDevice(Device):
    """Test generic device."""

    def _register_states(self):
        """Dummy abstract class."""

    def _register_handlers(self):
        """Dummy abstract class."""

    def _register_default_links(self):
        """Dummy abstract class."""


async def load_database():
    """Load the device databae."""
    plm = PLM(PORT)
    await plm.async_connect()

    for address in DEVICE_ADDRESSES:
        device = TestDevice(address, DEVICE_CAT, DEVICE_SUBCAT)

        _LOGGER.info('Starting DB load for %s', address)
        await device.aldb.async_load()
        _LOGGER.info('ALDB load status: %s', device.aldb.status.name)
        for mem_addr in device.aldb:
            _LOGGER.info(device.aldb[mem_addr])

    await plm.async_close()

def print_topics(topic=pub.AUTO_TOPIC, **kwargs):
    """Print all messages sent."""
    _LOGGER.debug('Topic: %s', topic)
    _LOGGER.debug('kwargs: %s', kwargs)


if __name__ == '__main__':
    stream_handler = logging.StreamHandler(sys.stdout)
    _LOGGER.addHandler(stream_handler)
    _LOGGER_PYINSTEON.addHandler(stream_handler)

    _LOGGER.setLevel(logging.INFO)
    _LOGGER_PYINSTEON.setLevel(logging.INFO)

    pub.subscribe(print_topics, pub.ALL_TOPICS)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Running database load method')
    loop.run_until_complete(load_database())
