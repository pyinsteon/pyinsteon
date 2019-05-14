"""Python module for controlling Insteon devices."""

from pubsub import pub
from .protocol import async_modem_connect
from .managers.device_manager import DeviceManager


devices = DeviceManager()


async def async_connect(device=None, host=None, port=None, username=None,
                        password=None, hub_version=2, **kwargs):
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
    modem = await async_modem_connect(device=device, host=host, port=port,
                                      username=username, password=password,
                                      hub_version=hub_version, **kwargs)
    devices.modem = modem
    devices.id_manager.start()
    return modem

async def async_close():
    """Close the connection and stop all tasks."""
    import asyncio
    await devices.modem.async_close()
    devices.id_manager.close()
    await asyncio.sleep(.1)
