"""Manage saving and restoring devices from JSON file"""
import json
import logging

from ..address import Address
from .device_manager import create_device, DeviceId

DEVICE_INFO_FILE = 'insteon_devices.json'
_LOGGER = logging.getLogger(__name__)


def _dict_to_device(device_dict):
    address = Address(device_dict.get('address'))
    aldb_status = device_dict.get('aldb_status', 0)
    aldb = device_dict.get('aldb', {})
    cat = device_dict.get('cat')
    subcat = device_dict.get('subcat')
    firmware = device_dict.get('firmware')
    operating_flags = device_dict.get('operating_flags')
    ext_properties = _dict_to_ext_properties(device_dict.get('ext_properties'))
    device_id = DeviceId(address, cat, subcat, firmware)
    device = create_device(device_id)
    if device:
        aldb_records = _dict_to_aldb_record(aldb)
        device.aldb.load_saved_records(aldb_status, aldb_records)
        if operating_flags:
            device.operating_flags.set_value(operating_flags)
        if ext_properties:
            device.ext_properties.set_values(ext_properties)
    return device


def _device_to_dict(device_list):
    """Convert a device to a dictionary."""
    from ..x10_address import X10Address

    devices = []
    for addr in device_list:
        device = device_list.get(addr)
        if not isinstance(device.address, X10Address):
            aldb = {}
            for mem in device.aldb:
                rec = device.aldb[mem]
                if rec:
                    aldbRec = {'memory': mem,
                               'control_flags': int(rec.control_flags),
                               'group': rec.group,
                               'address': rec.address.id,
                               'data1': rec.data1,
                               'data2': rec.data2,
                               'data3': rec.data3}
                    aldb[mem] = aldbRec
            ext_properties = {}
            index = 3
            for flag in device.ext_properties:
                ext_properties[flag] = {'value': device.ext_properties[flag],
                                        'index': index}
                index += 1
            deviceInfo = {'address': device.address.id,
                          'cat': device.cat,
                          'subcat': device.subcat,
                          'firmware': device.firmware,
                          'aldb_status': device.aldb.status.value,
                          'aldb': aldb,
                          'operating_flags': int(device.operating_flags),
                          'ext_properties': ext_properties}
            devices.append(deviceInfo)
    return devices


def _dict_to_aldb_record(aldb_dict):
    from ..aldb.control_flags import create_from_byte
    from ..aldb.aldb_record import ALDBRecord
    records = {}
    for mem_addr in aldb_dict:
        rec = aldb_dict[mem_addr]
        control_flags = create_from_byte(int(rec.get('control_flags', 0)))
        group = int(rec.get('group', 0))
        rec_addr = rec.get('address', '000000')
        data1 = int(rec.get('data1', 0))
        data2 = int(rec.get('data2', 0))
        data3 = int(rec.get('data3', 0))
        records[int(mem_addr)] = ALDBRecord(int(mem_addr), control_flags,
                                            group, rec_addr,
                                            data1, data2, data3)
    return records


def _dict_to_ext_properties(ext_properties_dict):
    from collections import OrderedDict
    if ext_properties_dict is None:
        return None
    kwargs = {}
    temp_data = {}
    data = OrderedDict()
    for flag in ext_properties_dict:
        prop_dict = ext_properties_dict[flag]
        index = prop_dict['index']
        key_name = 'data{}'.format(index)
        kwargs[key_name] = flag
        temp_data[index] = prop_dict['value']
    for index in range(3, 15):
        data[index] = temp_data[index]

    return data


class SavedDeviceManager():
    """Manage saving and restoring devices from JSON."""

    def __init__(self, workdir):
        """Init the SavedDeviceManager class."""
        self._workdir = workdir

    async def async_save(self, device_list: dict):
        """Save all devices to the `insteon_devices.json` file for faster loading."""
        device_dict = _device_to_dict(device_list)
        await self._write_saved_devices(device_dict)

    async def async_load(self) -> {}:
        """Load devices from the saved device file."""
        from .. import devices
        modem = devices.modem
        saved_devices = await self._read_saved_devices()
        devices = {}
        for saved_device in saved_devices:
            address = Address(saved_device.get('address'))
            if address != modem.address:
                device = _dict_to_device(saved_device)
                if device:
                    devices[address] = device
                    _LOGGER.debug('Device with id %s added to device list '
                                  'from saved device data.', address)
            else:
                aldb_status = saved_device.get('aldb_status', 0)
                aldb = saved_device.get('aldb', {})
                aldb_records = _dict_to_aldb_record(aldb)
                modem.aldb.load_saved_records(aldb_status, aldb_records)
        return devices

    async def _read_saved_devices(self):
        """Load device information from the device info file."""
        _LOGGER.debug("Loading saved device info.")
        from aiofile import AIOFile
        from os import path

        saved_devices = []
        if not self._workdir:
            _LOGGER.debug("Really Loading saved device info.")
            return saved_devices

        try:
            device_file = path.join(self._workdir, DEVICE_INFO_FILE)
            async with AIOFile(device_file, 'r') as afp:
                json_file = ''
                json_file = await afp.read()
            try:
                saved_devices = json.loads(json_file)
            except json.decoder.JSONDecodeError:
                _LOGGER.debug("Loading saved device file failed")
        except FileNotFoundError:
            _LOGGER.debug("Saved device file not found")
        return saved_devices

    async def _write_saved_devices(self, devices):
        from aiofile import AIOFile
        from os import path

        _LOGGER.debug('Writing %d devices to save file', len(devices))
        device_file = path.join(self._workdir, DEVICE_INFO_FILE)
        try:
            async with AIOFile(device_file, 'w') as afp:
                out_json = json.dumps(devices, indent=2)
                await afp.write(out_json)
                await afp.fsync()
        except FileNotFoundError as e:
            _LOGGER.error('Cannot write to file %s', device_file)
            _LOGGER.error('Exception: %s', str(e))
