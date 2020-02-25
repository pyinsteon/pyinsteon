"""Protocol classes to interface with serial, socket and http devices."""
import asyncio
import logging
from functools import partial

import serial

from .serial_transport import SerialTransport
from ..constants import MessageFlagType
from .http_transport import HttpTransport
from .protocol import Protocol
from ..handlers.get_im_info import GetImInfoHandler
from ..device_types.plm import PLM
from ..device_types.hub import Hub


_LOGGER = logging.getLogger(__name__)


def topic_to_message_type(topic):
    """Return MessageFlagType from the topic."""
    subtopics = topic.name.split(".")
    flag = "direct" if len(subtopics) < 3 else subtopics[2]
    for flag_type in MessageFlagType:
        if flag.lower() == str(flag_type):
            return flag_type
    return MessageFlagType(0)


def topic_to_message_handler(topic, register_list):
    """Register handler to topic."""

    def register(func):
        register_list["send.{}".format(topic)] = func
        return func

    return register


def topic_to_command_handler(topic, register_list):
    """Register handler to topic."""

    def register(func):
        register_list["send.{}".format(topic)] = func
        return func

    return register


async def async_connect_serial(device, protocol):
    """Connect to the PowerLine Modem via serial port.

    Parameters:
        port – Device name.
        protocol - Insteon Modem Protocol instance.

    """
    loop = asyncio.get_event_loop()
    try:
        ser = serial.serial_for_url(url=device, baudrate=19200)
        transport = SerialTransport(loop, protocol, ser, device=device)
    except OSError as ex:
        _LOGGER.warning("Unable to connect to %s: %s", device, ex)
        transport = None
    return transport


async def async_connect_socket(host, protocol, port=None):
    """Connect to the Hub Version 1 via TCP Socket."""

    port = 9761 if not port else port
    loop = asyncio.get_event_loop()
    url = "socket://{}:{}".format(host, port)
    ser = serial.serial_for_url(url=url, baudrate=19200)
    transport = SerialTransport(loop, protocol, ser, device=url)
    return transport


async def async_connect_http(host, username, password, protocol, port=None):
    """Connect to the Hub Version 2 via HTTP."""
    port = 25105 if not port else port
    transport = HttpTransport(
        protocol=protocol, host=host, port=port, username=username, password=password
    )
    if await transport.async_test_connection():
        protocol.connection_made(transport)
    return transport


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
    modem_address = "000000"
    modem_cat = 0x03
    modem_subcat = 0x00
    modem_firmware = 0x00

    def set_im_info(address, cat, subcat, firmware):
        nonlocal modem_address, modem_cat, modem_subcat, modem_firmware
        modem_address = address
        modem_cat = cat
        modem_subcat = subcat
        modem_firmware = firmware

    transport = None
    if not device and not host:
        return ValueError("Must specify either a device or a host")

    if device:
        Modem = PLM
        connect_method = partial(async_connect_serial, **{"device": device})
        protocol = Protocol(connect_method=connect_method)

    elif hub_version == 2:
        Modem = Hub
        connect_method = partial(
            async_connect_http,
            **{"host": host, "username": username, "password": password, "port": port},
        )
        protocol = Protocol(connect_method=connect_method)

    else:
        Modem = PLM
        connect_method = partial(async_connect_socket, **{"host": host, "port": port})
        protocol = Protocol(connect_method=connect_method)

    await protocol.async_connect()

    get_im_info = GetImInfoHandler()
    get_im_info.subscribe(set_im_info)
    # TODO check for success or failure
    await get_im_info.async_send()
    modem = Modem(
        address=modem_address,
        cat=modem_cat,
        subcat=modem_subcat,
        firmware=modem_firmware,
    )
    modem.protocol = protocol
    modem.transport = transport
    # Pause to allow connection_made to be called:
    return modem
