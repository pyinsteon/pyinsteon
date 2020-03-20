"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_close, async_connect, devices
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = "COM5"
USERNAME, PASSWORD, HOST = get_hub_config()
address = "13.36.96"


async def set_default_links():
    """Load the device databae."""
    # await async_connect(device=DEVICE)
    await async_connect(host=HOST, username=USERNAME, password=PASSWORD)

    await devices.async_load(workdir=PATH, id_devices=0)
    device = devices[address]

    set_log_levels(
        logger="info",
        logger_pyinsteon="info",
        logger_messages="info",
        logger_topics=True,
    )

    devices.modem.aldb.remove(controller=False, group=1, target=address)
    for mem_addr in device.aldb:
        rec = device.aldb[mem_addr]
        if rec.target == devices.modem.address and rec.group == 1:
            device.aldb.remove(mem_addr)

    await devices.modem.aldb.async_write()
    await device.aldb.async_write()

    await device.async_add_default_links()

    set_log_levels(
        logger="info",
        logger_pyinsteon="info",
        logger_messages="info",
        logger_topics=False,
    )

    await devices.modem.aldb.async_load()
    await device.aldb.async_load(refresh=True)

    _LOGGER.info("Modem Links")
    for mem_addr in devices.modem.aldb:
        _LOGGER.info(devices.modem.aldb[mem_addr])

    _LOGGER.info("Device Links")
    for mem_addr in devices[address].aldb:
        _LOGGER.info(device.aldb[mem_addr])
    await async_close()


if __name__ == "__main__":
    set_log_levels(
        logger="info",
        logger_pyinsteon="info",
        logger_messages="info",
        logger_topics=False,
    )
    loop = asyncio.get_event_loop()
    _LOGGER.info("Loading All-Link database for all devices")
    loop.run_until_complete(set_default_links())
