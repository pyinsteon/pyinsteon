"""Monitor all messages to and from the Insteon Modem."""
import asyncio

from pyinsteon import async_close, async_connect, devices
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()

def device_added(address):
    """Log a device added to the device list."""
    _LOGGER.info('Device added: %s', address)

async def run():
    """Run the monitoring."""
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='debug', logger_topics=True)
    await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    devices.subscribe(device_added)
    await devices.async_load(workdir=PATH)
    await devices.async_save(workdir=PATH)
    await devices.modem.async_get_configuration()
    await devices.modem.async_set_configuration(
        disable_auto_linking=devices.modem.disable_auto_linking, monitor_mode=True,
        auto_led=devices.modem.auto_led, deadman=devices.modem.deadman)
    _LOGGER.info('Devices loaded: %d', len(devices))
    try:
        while True:
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        await async_close()
        raise KeyboardInterrupt()


if __name__ == '__main__':
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
