"""Load saved devices to provide quick startup."""

import asyncio

from pyinsteon import async_close, async_connect
from pyinsteon.constants import AllLinkMode
from pyinsteon.managers.link_manager import async_enter_linking_mode
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = "COM5"
USERNAME, PASSWORD, HOST = get_hub_config()
done = asyncio.Queue()


async def async_setup_device(address):
    """Set up device."""
    from pyinsteon import devices

    device = devices[address]
    await device.aldb.async_load(refresh=True)
    await device.async_read_op_flags()
    await device.async_read_ext_properties()
    max_wait = 300
    wait = 0
    sleep_for = 5
    while not device.aldb.is_loaded and wait < max_wait:
        await asyncio.sleep(sleep_for)
        wait += sleep_for
    await device.async_add_default_links()
    await asyncio.sleep(sleep_for)
    await devices.async_save(workdir=PATH)
    done.put_nowait("done")


def device_added(address):
    """Call set up device."""
    asyncio.ensure_future(async_setup_device(address))


async def do_run():
    """Connect to the PLM and load the ALDB."""
    # devices = await async_connect(device=DEVICE)
    devices = await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    await devices.async_load(workdir=PATH, id_devices=0)
    devices.subscribe(device_added)
    await async_enter_linking_mode(link_mode=AllLinkMode.EITHER, group=0)
    _LOGGER.info("Press device SET button")
    await done.get()
    await async_close()


if __name__ == "__main__":
    set_log_levels(
        logger="info",
        logger_pyinsteon="True",
        logger_messages="debug",
        logger_topics=True,
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_run())
