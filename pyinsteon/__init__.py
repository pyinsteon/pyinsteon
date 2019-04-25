"""Python module for controlling Insteon devices."""

from pubsub import pub
from .protocol import async_modem_connect
from .devices.device_manager import DeviceManager


device_mgr = DeviceManager()


async def async_connect(device=None, host=None, port=None, username=None,
                        password=None, hub_version=2, **kwargs):
    modem = await async_modem_connect(device=device, host=host, port=port,
                                      username=username, password=password,
                                      hub_version=hub_version, **kwargs)
    device_mgr.modem = modem
    return modem
