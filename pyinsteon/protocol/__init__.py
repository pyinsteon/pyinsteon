"""Protocol classes to interface with serial, socket and http devices."""
import asyncio
import logging
from functools import partial

from pyinsteon.constants import ResponseStatus

from ..handlers.get_im_info import GetImInfoHandler
from ..managers.device_id_manager import DeviceId
from ..managers.utils import create_device
from .http_transport import async_connect_http
from .protocol import Protocol
from .serial_transport import async_connect_serial, async_connect_socket

_LOGGER = logging.getLogger(__name__)


async def async_modem_connect(
    device=None, host=None, port=None, username=None, password=None, hub_version=2
):
    """Connect to the Insteon Modem.

    Returns an Insteon Modem object (PLM, Hub, or Hub1)

    Parameters:
        device: Serial port device (i.e. /dev/ttyUSB0 or COM5)
        host: Hub IP address (i.e. 192.168.1.100)
        port: Hub port number (Default 25105 for version 2 or 9761 for version 1)
        username: Hub username for the Hub V2
        password: Hub password for the Hub V2
        hub_version: 1 | 2 (Default: 2)

    If the device is a serial device see the serial class parameters.

    """
    device_id = None

    def set_im_info(address, cat, subcat, firmware):
        nonlocal device_id
        device_id = DeviceId(address, cat, subcat, firmware)

    async def async_test_device_id():
        """Test if the device ID is set."""
        nonlocal device_id
        retries = 10
        while device_id is None and retries:
            await asyncio.sleep(0.1)
            if device_id is not None:
                return True
            retries -= 1
        return False

    transport = None
    if not device and not host:
        raise ValueError("Must specify either a device or a host")

    if device:
        connect_method = partial(async_connect_serial, **{"device": device})
        protocol = Protocol(connect_method=connect_method)

    elif hub_version == 2:
        connect_method = partial(
            async_connect_http,
            **{"host": host, "username": username, "password": password, "port": port},
        )
        protocol = Protocol(connect_method=connect_method)

    else:
        connect_method = partial(async_connect_socket, **{"host": host, "port": port})
        protocol = Protocol(connect_method=connect_method)

    try:
        await protocol.async_connect(retry=False)
    except ConnectionError:
        raise ConnectionError("Modem did not respond connection request")

    get_im_info = GetImInfoHandler()
    get_im_info.subscribe(set_im_info)
    retries = 5
    result = None
    while retries and result != ResponseStatus.SUCCESS:
        await asyncio.sleep(1)
        result = await get_im_info.async_send()
        retries -= 1

    # Wait for a max of 60 seconds for the modem to respond
    if device_id is None and not await async_test_device_id():
        raise ConnectionError("Modem did not respond to ID request")

    modem = create_device(device_id)
    modem.protocol = protocol
    modem.transport = transport
    return modem
