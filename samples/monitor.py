"""Monitor all messages to and from the Insteon Modem."""
import asyncio
from pyinsteon import async_connect, async_close, devices
from samples import get_hub_config, set_log_levels, PATH, get_hub_config


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()

async def run():
    """Run the monitoring."""
    set_log_levels(logger='info', logger_pyinsteon='info', logger_messages='debug')
    await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    await devices.async_load(workdir=PATH, id_devices=0)
    await devices.async_save(workdir=PATH)
    while True:
        await asyncio.sleep(600)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        close_task = loop.create_task(async_close())
        loop.run_until_complete(close_task)
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
