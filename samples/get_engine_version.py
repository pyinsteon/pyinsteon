"""Load saved devices to provide quick startup."""

import asyncio

import async_timeout
import utils

from pyinsteon import async_close, async_connect
from pyinsteon.address import Address
from pyinsteon.constants import EngineVersion, ResponseStatus
from pyinsteon.handlers.to_device.engine_version_request import EngineVersionRequest

# DEVICE = '/dev/ttyS5'
DEVICE = "COM5"
USERNAME, PASSWORD, HOST, PORT = utils.get_hub_config()

_engine_version_queue = asyncio.Queue()


async def _handle_engine_version_response(engine_version):
    """Handle the engine version response."""
    await _engine_version_queue.put(engine_version)


async def do_run():
    """Connect to the PLM and load the ALDB."""
    # await async_connect(device=DEVICE)
    await async_connect(host=HOST, username=USERNAME, password=PASSWORD, port=PORT)
    addrs = [
        Address("14.5F.D7"),  # I2 device
        Address("14.60.2F"),  # I2 device
        Address("14.61.9B"),  # I2 device
        Address("14.61.9B"),  # I2 device
        Address("14.61.B6"),  # I2 device
        Address("14.61.B7"),  # I2 device
        Address("14.61.C0"),  # I2 device
        Address("14.62.7A"),  # I2 device
        Address("26.7F.61"),  # i2CS?
        Address("26.7f.8D"),  # i2CS?
        Address("27.C3.87"),  # i2CS?
        Address("2C.35.8F"),  # i2CS?
        Address("41.89.3F"),  # i2CS Outlet
        Address("41.89.76"),  # i2CS Outlet
        Address("41.89.CF"),  # i2CS Outlet
        Address("41.8A.16"),  # i2CS Outlet
        Address("48.88.47"),  # i2CS Outlet
        Address("48.88.48"),  # i2CS Outlet
        Address("45.31.3B"),  # i2CS IOLinc
        Address("60.1B.37"),  # i3 Dial
    ]
    for addr in addrs:
        addr = Address(addr)
        cmd = EngineVersionRequest(address=addr)
        cmd.subscribe(_handle_engine_version_response)
        response = None
        retries = 3
        while (
            response
            not in [
                ResponseStatus.SUCCESS,
                ResponseStatus.DIRECT_NAK_ALDB,
                ResponseStatus.DIRECT_NAK_PRE_NAK,
            ]
            and retries
        ):
            response = await cmd.async_send()
            retries -= 1
        str_respn = str(response)
        version = EngineVersion.UNKNOWN
        if response == ResponseStatus.SUCCESS:
            try:
                async with async_timeout.timeout(1):
                    version = await _engine_version_queue.get()
            except asyncio.TimeoutError:
                pass
        elif response in [
            ResponseStatus.DIRECT_NAK_ALDB,
            ResponseStatus.DIRECT_NAK_PRE_NAK,
        ]:
            version = EngineVersion.I2CS
        print(addr, str_respn, str(version))
    await async_close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
