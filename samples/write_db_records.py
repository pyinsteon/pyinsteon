"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_close, async_connect, devices
from pyinsteon.aldb.aldb_record import ALDBRecord
from samples import _LOGGER, PATH, get_hub_config, set_log_levels

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()



async def set_default_links():
    """Load the device databae."""
    await async_connect(device=DEVICE)
    # await async_connect(host=HOST,
    #                     username=USERNAME,
    #                     password=PASSWORD)

    await devices.async_load(workdir=PATH, id_devices=0)
    await devices.async_save(workdir=PATH)
    set_log_levels(logger='info', logger_pyinsteon='debug',
                   logger_messages='debug', logger_topics=True)

    address = "133696"
    device = devices[address]
    rec_0fd7 = ALDBRecord(memory=0x0fb7, controller=False, group=0, target='00.00.00',
                          data1=0, data2=0, data3=0, in_use=False, bit5=False, bit4=False,
                          high_water_mark=True)
    device.aldb[0x0fb7] = rec_0fd7
    await device.aldb.async_write()
    await device.aldb.async_load(refresh=True)
    await devices.async_save(workdir=PATH)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=False)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(set_default_links())
