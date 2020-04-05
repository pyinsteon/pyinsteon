"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_close, async_connect
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = "COM3"
USERNAME, PASSWORD, HOST, PORT = get_hub_config()


async def load_device_properties():
    """Load the device databae."""
    devices = await async_connect(device=DEVICE)
    # devices = await async_connect(host=HOST,
    #                              username=USERNAME,
    #                              password=PASSWORD)

    await devices.async_load(workdir=PATH)
    await devices.async_save(workdir=PATH)
    addresses = ["13.36.96", "45.31.94"]
    for address in addresses:
        device = devices[address]
        await device.aldb.async_load(refresh=True)
        _LOGGER.info(
            "ALDB load status for %s: %s", device.address, device.aldb.status.name
        )
        _LOGGER.info("Loading device properties")
        await device.async_read_op_flags()
        await device.async_read_ext_properties()
        await asyncio.sleep(3)  # Give the device some time to respond to get ext prop

        await devices.async_save(workdir=PATH)
        _LOGGER.info("")
        for mem_addr in device.aldb:
            rec = device.aldb[mem_addr]
            _LOGGER.info(rec)
    await async_close()


if __name__ == "__main__":
    set_log_levels(
        logger="info",
        logger_pyinsteon="info",
        logger_messages="info",
        logger_topics=True,
    )
    loop = asyncio.get_event_loop()
    _LOGGER.info("Loading All-Link database for all devices")
    loop.run_until_complete(load_device_properties())
