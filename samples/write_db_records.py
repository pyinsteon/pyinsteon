"""Sample program to demonstrate loading a device All-Link Database."""
import asyncio

from pyinsteon import async_connect, devices, async_close
from pyinsteon.aldb.aldb_record import ALDBRecord
from samples import set_log_levels, _LOGGER, PATH, get_hub_config

# DEVICE = '/dev/ttyS5'
DEVICE = 'COM5'
USERNAME, PASSWORD, HOST = get_hub_config()



async def set_default_links():
    """Load the device databae."""
    # await async_connect(device=DEVICE)
    await async_connect(host=HOST,
                        username=USERNAME,
                        password=PASSWORD)

    await devices.async_load(workdir=PATH, id_devices=0)
    await devices.async_save(workdir=PATH)
    set_log_levels(logger='info', logger_pyinsteon='debug',
                   logger_messages='debug', logger_topics=True)

    address = "133696"
    device = devices[address]
    rec_4079 = ALDBRecord(memory=0x0fe7, controller=False, group=0x25, target='31.18.A2',
                          data1=125, data2=28, data3=1, in_use=True, bit5=True)
    rec_0fbf = ALDBRecord(memory=0x0fbf, controller=False, group=0, target='00.00.00',
                          data1=0, data2=0, data3=0, in_use=False, bit5=False, bit4=False,
                          high_water_mark=True)
    device.aldb[4079] = rec_4079
    device.aldb[0x0fbf] = rec_0fbf
    await device.aldb.async_write_records()
    await device.aldb.async_load(refresh=True)
    await devices.async_save(workdir=PATH)
    await async_close()


if __name__ == '__main__':
    set_log_levels(logger='info', logger_pyinsteon='info',
                   logger_messages='info', logger_topics=False)
    loop = asyncio.get_event_loop()
    _LOGGER.info('Loading All-Link database for all devices')
    loop.run_until_complete(set_default_links())
