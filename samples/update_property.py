"""Monitor all messages to and from the Insteon Modem."""
import asyncio
from pyinsteon import async_connect, async_close, devices
from samples import get_hub_config, set_log_levels, PATH, _LOGGER


# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()

def device_added(address):
    """Log a device added to the device list."""
    _LOGGER.info('Device added: %s', address)

async def run():
    """Run the monitoring."""
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=True)
    # await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    await async_connect(device=DEVICE)
    devices.subscribe(device_added)
    await devices.async_load(workdir=PATH, id_devices=0)
    await devices.async_save(workdir=PATH)

    address = '133696'
    device = devices[address]

    if device:
        await device.async_read_op_flags()
        await device.async_read_ext_properties()
        from pyinsteon.operating_flag import LED_BLINK_ON_TX_ON
        from pyinsteon.extended_property import RAMP_RATE
        _LOGGER.info('LED_BLINK_ON_TX_ON: %s', device.operating_flags[LED_BLINK_ON_TX_ON].value)
        _LOGGER.info('RAMP_RATE: %s',  device.properties[RAMP_RATE].value)

        device.operating_flags[LED_BLINK_ON_TX_ON].new_value = True
        device.properties[RAMP_RATE].new_value = 28

        await device.async_write_op_flags()
        await device.async_write_ext_properties()
        await device.async_read_op_flags()
        await device.async_read_ext_properties()
        _LOGGER.info('LED_BLINK_ON_TX_ON: %s', device.operating_flags[LED_BLINK_ON_TX_ON].value)
        _LOGGER.info('RAMP_RATE: %s',  device.properties[RAMP_RATE].value)
    else:
        _LOGGER.info('No device found for address: %s', address)
    await async_close()

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
