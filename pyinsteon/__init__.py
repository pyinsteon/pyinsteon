"""Python module for controlling Insteon devices."""

from pubsub import pub
from .protocol import async_modem_connect
from .devices.device_manager import DeviceManager


device_mgr = DeviceManager()


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
    device_mgr.modem = modem
    return modem
