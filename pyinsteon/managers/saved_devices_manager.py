"""Manage saving and restoring devices from JSON file."""
import json
import logging
from os import path

from aiofile import AIOFile

from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..x10_address import X10Address
from .device_id_manager import DeviceId
from .utils import create_device

DEVICE_INFO_FILE = "insteon_devices.json"
OLD_DEVICE_INFO_FILE = "insteon_plm_device_info.dat"
_LOGGER = logging.getLogger(__name__)


def _dict_to_device(device_dict):
    address = Address(device_dict.get("address"))
    aldb_status = device_dict.get("aldb_status", 0)
    aldb = device_dict.get("aldb", {})
    cat = device_dict.get("cat")
    subcat = device_dict.get("subcat")
    firmware = device_dict.get("firmware")
    operating_flags = device_dict.get("operating_flags", {})
    properties = device_dict.get("properties", {})
    device_id = DeviceId(address, cat, subcat, firmware)
    device = create_device(device_id)
    if device:
        aldb_records = _dict_to_aldb_record(aldb)
        device.aldb.load_saved_records(aldb_status, aldb_records)
        for flag in operating_flags:
            value = operating_flags[flag]
            if device.operating_flags.get(flag):
                device.operating_flags[flag].load(value)
        for flag in properties:
            value = properties[flag]
            if device.properties.get(flag):
                device.properties[flag].load(value)
    return device


def _device_to_dict(device_list):
    """Convert a device to a dictionary."""
    device_dict = []
    for addr in device_list:
        device = device_list.get(addr)
        if not isinstance(device.address, X10Address):
            aldb = {}
            for mem in device.aldb:
                rec = device.aldb[mem]
                if rec:
                    aldb_rec = {
                        "memory": mem,
                        "in_use": rec.is_in_use,
                        "controller": rec.is_controller,
                        "high_water_mark": rec.is_high_water_mark,
                        "bit5": rec.is_bit5_set,
                        "bit4": rec.is_bit4_set,
                        "group": rec.group,
                        "target": rec.target.id,
                        "data1": rec.data1,
                        "data2": rec.data2,
                        "data3": rec.data3,
                    }
                    aldb[mem] = aldb_rec
            operating_flags = {}
            for flag in device.operating_flags:
                operating_flags[flag] = device.operating_flags[flag].value
            properties = {}
            for flag in device.properties:
                properties[flag] = device.properties[flag].value
            device_info = {
                "address": device.address.id,
                "cat": device.cat,
                "subcat": device.subcat,
                "firmware": device.firmware,
                "aldb_status": device.aldb.status.value,
                "aldb": aldb,
                "operating_flags": operating_flags,
                "properties": properties,
            }
            device_dict.append(device_info)
    return device_dict


def _dict_to_aldb_record(aldb_dict):
    records = {}
    for mem_addr in aldb_dict:
        rec = aldb_dict[mem_addr]
        memory = int(mem_addr)
        control_flags = int(rec.get("control_flags", 0))
        in_use = rec.get("in_use", bool(control_flags & 1 << 7))
        controller = rec.get("controller", bool(control_flags & 1 << 6))
        bit5 = rec.get("bit5", bool(control_flags & 1 << 5))
        bit4 = rec.get("bit4", bool(control_flags & 1 << 4))
        high_water_mark = rec.get("high_water_mark", not bool(control_flags & 1 << 1))
        group = int(rec.get("group", 0))
        target = rec.get("target", rec.get("address", "000000"))
        data1 = int(rec.get("data1", 0))
        data2 = int(rec.get("data2", 0))
        data3 = int(rec.get("data3", 0))
        records[memory] = ALDBRecord(
            memory=memory,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            in_use=in_use,
            high_water_mark=high_water_mark,
            bit5=bit5,
            bit4=bit4,
        )
    return records


def _convert_old_device_dict(old_device_dict):
    """Convert insteonplm saved device file to new device file."""
    new_device_dict = old_device_dict
    old_product_key = old_device_dict.get("firmware")
    old_product_key = old_device_dict.get("product_key", old_product_key)
    new_device_dict["firmware"] = old_product_key
    old_aldb_status = old_device_dict.get("aldb_status", 0)
    old_aldb = new_device_dict.get("aldb", {})
    new_device_dict["aldb_status"] = _convert_old_aldb_status(old_aldb_status)
    new_device_dict["aldb"] = _convert_old_aldb(old_aldb)
    return new_device_dict


def _convert_old_aldb_status(old_status):
    """Convert insteonplm ALDB load status to new ALDB load status.

    Old status values:
        EMPTY = 0
        LOADING = 1
        LOADED = 2
        FAILED = 3
        PARTIAL = 4

    New status values:
        EMPTY = 0
        LOADED = 1
        LOADING = 2
        FAILED = 3
        PARTIAL = 4
    """
    if old_status in [0, 3, 4]:
        return old_status
    if old_status == 1:
        return 2
    if old_status == 2:
        return 1


def _convert_old_aldb(old_aldb):
    """Convert insteonplm ALDB to new ALDB."""
    new_aldb = {}
    for mem_addr in old_aldb:
        rec = old_aldb[mem_addr]
        control_flags = int(rec.get("control_flags", 0))
        in_use = rec.get("in_use", bool(control_flags & 1 << 7))
        controller = rec.get("controller", bool(control_flags & 1 << 6))
        bit5 = rec.get("bit5", bool(control_flags & 1 << 5))
        bit4 = rec.get("bit4", bool(control_flags & 1 << 4))
        high_water_mark = rec.get("high_water_mark", not bool(control_flags & 1 << 1))
        group = int(rec.get("group", 0))
        target = rec.get("address", "000000")
        data1 = int(rec.get("data1", 0))
        data2 = int(rec.get("data2", 0))
        data3 = int(rec.get("data3", 0))

        new_aldb[mem_addr] = {
            "memory": mem_addr,
            "in_use": in_use,
            "controller": controller,
            "high_water_mark": high_water_mark,
            "bit5": bit5,
            "bit4": bit4,
            "group": group,
            "target": target,
            "data1": data1,
            "data2": data2,
            "data3": data3,
        }
    return new_aldb


class SavedDeviceManager:
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
        device_list = {}
        for saved_device in saved_devices:
            address = Address(saved_device.get("address"))
            if address != modem.address:
                device = _dict_to_device(saved_device)
                if device:
                    device_list[address] = device
                    _LOGGER.debug(
                        "Device with id %s added to device list "
                        "from saved device data.",
                        address,
                    )
            else:
                aldb_status = saved_device.get("aldb_status", 0)
                aldb = saved_device.get("aldb", {})
                aldb_records = _dict_to_aldb_record(aldb)
                modem.aldb.load_saved_records(aldb_status, aldb_records)
        return device_list

    async def _read_saved_devices(self):
        """Load device information from the device info file."""
        _LOGGER.debug("Loading saved device info.")

        saved_devices = []
        if not self._workdir:
            _LOGGER.debug("Really Loading saved device info.")
            return saved_devices

        try:
            device_file = path.join(self._workdir, DEVICE_INFO_FILE)
            async with AIOFile(device_file, "r") as afp:
                json_file = ""
                json_file = await afp.read()
            try:
                saved_devices = json.loads(json_file)
            except json.decoder.JSONDecodeError:
                _LOGGER.debug("Loading saved device file failed")
        except FileNotFoundError:
            _LOGGER.debug("Saved device file not found")
            saved_devices = await self._read_old_device_file()
        return saved_devices

    async def _write_saved_devices(self, device_list):

        _LOGGER.debug("Writing %d devices to save file", len(device_list))
        device_file = path.join(self._workdir, DEVICE_INFO_FILE)
        try:
            async with AIOFile(device_file, "w") as afp:
                out_json = json.dumps(device_list, indent=2)
                await afp.write(out_json)
                await afp.fsync()
        except FileNotFoundError as ex:
            _LOGGER.error("Cannot write to file %s", device_file)
            _LOGGER.error("Exception: %s", str(ex))

    async def _read_old_device_file(self):
        """Load device information from the insteonplm device info file."""
        _LOGGER.debug("Loading insteonplm saved device info.")

        saved_devices = []
        if not self._workdir:
            _LOGGER.debug("Really Loading saved device info.")
            return saved_devices

        try:
            device_file = path.join(self._workdir, OLD_DEVICE_INFO_FILE)
            async with AIOFile(device_file, "r") as afp:
                json_file = ""
                json_file = await afp.read()
            try:
                saved_devices = json.loads(json_file)
            except json.decoder.JSONDecodeError:
                _LOGGER.debug("Loading insteonplm saved device file failed")
        except FileNotFoundError:
            _LOGGER.debug("insteonplm saved device file not found")
        return _convert_old_device_dict(saved_devices)
