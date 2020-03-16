"""Monitor all messages to and from the Insteon Modem."""
import asyncio

from pyinsteon import async_close, async_connect, devices
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = "COM5"
USERNAME, PASSWORD, HOST = get_hub_config()


def device_added(address):
    """Log a device added to the device list."""
    _LOGGER.info("Device added: %s", address)


async def run():
    """Run the monitoring."""
    set_log_levels(
        logger="error",
        logger_pyinsteon="error",
        logger_messages="debug",
        logger_topics=False,
    )
    await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    await devices.async_load(workdir=PATH, id_devices=0, refresh=True)
    await devices.async_save(workdir=PATH)
    print(
        "'memory','in_use','controller','high_water_mark','bit5','bit4','group','target','data1','data2','data3'"
    )

    for addr in devices.modem.aldb:
        rec = devices.modem.aldb[addr]
        print(
            "{},{},{},{},{},{},{},{},{},{},{}".format(
                rec.mem_addr,
                rec.is_in_use,
                rec.is_controller,
                rec.is_high_water_mark,
                rec.is_bit5_set,
                rec.is_bit4_set,
                rec.group,
                rec.target.id,
                rec.data1,
                rec.data2,
                rec.data3,
            )
        )

    await async_close()


def run_main():
    """Run the tasks."""
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        loop.stop()
        pending = asyncio.Task.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
            try:
                loop.run_until_complete(task)
            except asyncio.CancelledError:
                pass
            except KeyboardInterrupt:
                pass
        loop.close()


if __name__ == "__main__":
    run_main()
