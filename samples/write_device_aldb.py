"""Monitor all messages to and from the Insteon Modem."""
import asyncio

from pyinsteon import async_close, async_connect, devices
from pyinsteon.aldb.aldb_record import ALDBRecord
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
    # await async_connect(device=DEVICE)
    await async_connect(host=HOST, username=USERNAME, password=PASSWORD)
    await devices.async_load(workdir=PATH, id_devices=0)

    address = '133696'
    device = devices[address]

    modem1 = '19.1A.60'
    modem2 = '31.18.A2'
    modem3 = '31.3E.1E'


    rec_0fff = ALDBRecord(0x0fff, False, 0, modem1, 0, 0, 0, bit5=True)
    rec_0ff7 = ALDBRecord(0x0ff7, True, 1, modem1, 0, 0, 0, bit5=True)

    rec_0fef = ALDBRecord(0x0fef, False, 0, modem2, 0, 0, 0, bit5=True)
    rec_0fe7 = ALDBRecord(0x0fe7, True, 1, modem2, 0, 0, 0, bit5=True)

    rec_0fdf = ALDBRecord(0x0fdf, False, 0, modem3, 0, 0, 0, bit5=True)
    rec_0fd7 = ALDBRecord(0x0fd7, True, 1, modem3, 0, 0, 0, bit5=True)

    rec_0fcf = ALDBRecord(0x0fcf, False, 0, '00.00.00', 0, 0, 0, bit5=False, bit4=False, in_use=False, high_water_mark=True)


    device.aldb[0x0fff] = rec_0fff
    device.aldb[0x0ff7] = rec_0ff7

    device.aldb[0x0fef] = rec_0fef
    device.aldb[0x0fe7] = rec_0fe7

    device.aldb[0x0fdf] = rec_0fdf
    device.aldb[0x0fd7] = rec_0fd7

    device.aldb[0x0fcf] = rec_0fcf

    await device.aldb.async_write()

    await device.aldb.async_load(refresh=True)

    await devices.async_save(workdir=PATH)

    print("'memory','in_use','controller','high_water_mark','bit5','bit4','group','target','data1','data2','data3'")

    for addr in device.aldb:
        rec = device.aldb[addr]
        print(rec)

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
