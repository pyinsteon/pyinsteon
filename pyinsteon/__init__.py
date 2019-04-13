"""Python module for controlling Insteon devices."""

from pubsub import pub
from .protocol import async_modem_connect

async def async_connect(device=None, host=None, port=None, username=None,
                        password=None, hub_version=2, **kwargs):
    """Connect to the Insteon Modem and return a Hub or a PLM."""
    modem = await async_modem_connect(device=device, host=host, port=port,
                                      username=username, password=password,
                                      hub_version=hub_version, **kwargs)
    return modem
