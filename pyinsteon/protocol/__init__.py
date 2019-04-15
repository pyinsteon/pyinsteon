"""Protocol classes to interface with serial, socket and http devices."""
import asyncio
from functools import partial

from .. import pub


def topic_to_message_handler(topic):
    """Decorator to register handler to topic."""
    def register(func):
        pub.subscribe(func, 'send.{}'.format(topic))
        return func
    return register


def topic_to_command_handler(topic):
    """Decorator to register handler to topic."""
    def register(func):
        pub.subscribe(func, 'send.{}'.format(topic))
        return func
    return register


async def async_connect_serial(device, protocol):
    """Connect to the PowerLine Modem via serial port.

    Parameters:

        port – Device name.
        protocol - Insteon Modem Protocol instance.
    """
    import serial
    from .serial_transport import SerialTransport
    loop = asyncio.get_event_loop()
    try:
        ser = serial.serial_for_url(url=device, baudrate=19200)
        transport = SerialTransport(loop, protocol, ser, device=device)
    except OSError:
        transport = None
    return transport


async def async_connect_socket(host, protocol, port=None):
    """Connect to the Hub Version 1 via TCP Socket."""
    import serial
    from .serial_transport import SerialTransport
    port = 9761 if not port else port
    loop = asyncio.get_event_loop()
    url = 'socket://{}:{}'.format(host, port)
    ser = serial.serial_for_url(url=url, baudrate=19200)
    transport = SerialTransport(loop, protocol, ser, device=url)
    return transport


async def async_connect_http(host, username, password, protocol, port=None):
    """Connect to the Hub Version 2 via HTTP."""
    from .http_transport import HttpTransport
    port = 25105 if not port else port
    loop = asyncio.get_event_loop()
    transport = HttpTransport(protocol=protocol, host=host, port=port,
                              username=username, password=password, loop=loop)
    if await transport.async_test_connection():
        protocol.connection_made(transport)
    return transport


async def async_modem_connect(device=None, host=None, port=None, username=None,
                              password=None, hub_version=2, workdir=''):
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
    from .protocol import Protocol
    from ..handlers.get_im_info import GetImInfoHandler
    address = '000000'
    cat = 0x03
    subcat = 0x00
    firmware = 0x00

    def set_im_info(address_in, cat_in, subcat_in, firmware_in):
        nonlocal address, cat, subcat, firmware
        address = address_in
        cat = cat_in
        subcat = subcat_in
        firmware = firmware_in

    transport = None
    if not device and not host:
        return ValueError('Must specify either a device or a host')

    if device:
        from ..devices.plm import PLM as Modem
        connect_method = partial(async_connect_serial, **{'device':device})
        protocol = Protocol(connect_method=connect_method)

    elif hub_version == 2:
        from ..devices.hub import Hub as Modem
        connect_method = partial(async_connect_http, **{'host':host,
                                                        'username':username,
                                                        'password':password,
                                                        'port':port})
        protocol = Protocol(connect_method=connect_method)

    else:
        from ..devices.plm import PLM as Modem
        connect_method = partial(async_connect_socket, **{'host':host,
                                                          'port':port,
                                                          'protocol':protocol})
        protocol = Protocol(connect_method=connect_method)

    await protocol.async_connect()

    get_im_info = GetImInfoHandler()
    get_im_info.subscribe(set_im_info)
    await get_im_info.async_send()
    modem = Modem(protocol=protocol, transport=transport, workdir=workdir,
                  address=address, cat=cat, subcat=subcat, firmware=firmware)
    # Pause to allow connection_made to be called:
    return modem
