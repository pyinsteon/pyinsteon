"""Load saved devices to provide quick startup."""

import asyncio

from pyinsteon import async_close, async_connect
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = "COM5"
USERNAME, PASSWORD, HOST = get_hub_config()


def state_changed(name, address, value, group):
    """Capture the state change."""
    _LOGGER.info("State changed to %s", value)


async def do_run():
    """Connect to the PLM and load the ALDB."""
    # devices = await async_connect(device=DEVICE)
    devices = await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    modem = devices.modem
    _LOGGER.info("Connected")
    _LOGGER.info("Modem Address: %s", modem.address)
    await devices.async_load(workdir=PATH, id_devices=0)
    device = devices["13.36.96"]
    device.groups[1].subscribe(state_changed)
    await device.async_on()
    await asyncio.sleep(1)
    await device.async_off()

    _LOGGER.info("Please manually turn device on and off.")
    await asyncio.sleep(20)

    _LOGGER.info("Getting device status.")
    await device.async_status()
    await async_close()


if __name__ == "__main__":
    set_log_levels(
        logger="info",
        logger_pyinsteon="info",
        logger_messages="info",
        logger_topics=False,
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
