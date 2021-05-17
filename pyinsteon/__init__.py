"""Python module for controlling Insteon devices."""
import asyncio
import logging

from pubsub import pub

from .handlers.from_device.x10_received import X10Received
from .listener_exception_handler import ListenerExceptionHandler
from .managers.device_manager import DeviceManager

# pylint: disable=unused-import
from .managers.x10_manager import async_x10_all_lights_off  # noqa: F401
from .managers.x10_manager import async_x10_all_lights_on  # noqa: F401
from .managers.x10_manager import async_x10_all_units_off  # noqa: F401
from .protocol import async_modem_connect

_LOGGER_TOPICS = logging.getLogger("pyinsteon.topics")
X10_RECEIVED_HANDLER = X10Received()

devices = DeviceManager()


async def async_connect(
    device=None,
    host=None,
    port=None,
    username=None,
    password=None,
    hub_version=2,
    **kwargs,
):
    """Connect to the Insteon Modem.

    Parameters:
        device: PLM serial / USB device name
        host: Hub hostname or IP address
        port: Hub TCP port
        username: Hub v2 username
        password: Hub v2 password
        hub_version: Hub version (default=2)

    Returns an Insteon Modem (PLM or Hub).

    """
    modem = await async_modem_connect(
        device=device,
        host=host,
        port=port,
        username=username,
        password=password,
        hub_version=hub_version,
        **kwargs,
    )
    devices.modem = modem
    devices.id_manager.start()
    return devices


async def async_close():
    """Close the connection and stop all tasks."""
    await devices.modem.async_close()
    for addr in devices:
        if devices[addr].is_battery:
            devices[addr].close()
    devices.id_manager.close()
    await asyncio.sleep(0.1)


def set_exception_handler():
    """Set the pubsub exception handler.

    This should only be run for debugging purposes.
    """
    pub.setListenerExcHandler(ListenerExceptionHandler())


def _log_all_topics(topic=pub.AUTO_TOPIC, **kwargs):
    """Log all topics from pyinsteon."""
    _LOGGER_TOPICS.debug("Topic: %s data: %s", topic.name, kwargs)


pub.subscribe(_log_all_topics, pub.ALL_TOPICS)
