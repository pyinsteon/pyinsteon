"""Device manager."""
import json
import logging

from . import Device
from ..address import Address
from .id_manager import DeviceId

DEVICE_INFO_FILE = 'insteon_devices.json'
_LOGGER = logging.getLogger(__name__)


class DeviceManager():
    """Manages the list of active devices."""

    def __init__(self):
        """Init the DeviceManager class."""
        self._devices = {}
        self._modem = None
        self._overrides = {}
        self._known_devices = None
        self._workdir = None

    def __getitem__(self, address):
        """Return a a device from the device address."""
        address = Address(address)
        return self._devices.get(address.id)

    def __iter__(self):
        """Return an iterator of devices."""
        for address in self._devices:
            yield address

    def get(self, address):
        """Return a device from an address."""
        return self._devices.get(address.id)

    def __additem__(self, device):
        """Add a device to the device list."""
        if isinstance(device, DeviceId):
            self._create_device(device)
        elif isinstance(device, Device):
            self._devices[device.address.id] = device
        else:
            raise ValueError('Device must be a DeviceId or a Device type.')

    @property
    def modem(self):
        """Return the Insteon Modem."""
        return self._modem

    @modem.setter
    def modem(self, value):
        """Set the Insteon Modem."""
        from ..devices.modem_base import ModemBase
        if not isinstance(value, ModemBase):
            raise ValueError
        self._modem = value
        self._devices[self._modem.address.id] = self._modem

    def add_override(self, address: Address, cat: int, subcat: int, firmware: int):
        """Add a device override to identify the device information.

        Typical use is to identify devices that do not respond to an ID Request
        such as a battery opperated device.
        """
        address = Address(address)
        self._overrides[address.id] = DeviceId(address, cat, subcat, firmware)

    async def discover_devices(self, address_list, ignore_known_devices=True):
        """Discover devices in the All-Link Database using ID Request command."""
        from .id_manager import IdManager
        mgr = IdManager()
        device_list = await mgr.async_id_devices(address_list, ignore_known_devices)
        for address in device_list:
            self._create_device(device_list[address])

    async def load_devices(self, workdir='', id_devices=1, force_reload=False):
        """Load devices from the `insteon_devices.yaml` file and device overrides.

        Parameters:
            workdir: Directory name to find the `insteon_devices.json` file

            id_devices: Indicate if devices should be identified using ID Request
                0: No devices are identified
                1: Unknown devices are identified
                2: All devices are identified
            (default=1)

            force_reload: Bool to indicate if the Modem ALDB should be reloaded to identify
            new devices (Default=False)

        The Modem ALDB is loaded if force_reload is True or if the saved file has no devices.
        """
        self._workdir = workdir if workdir else self._workdir
        if self._workdir:
            await self._load_saved_devices()

        if len(self._devices) == 1 or force_reload:
            # No devices were found in the saved devices file or reload_aldb is required
            await self._modem.aldb.async_load()

        if id_devices:
            address_list = []
            for mem_addr in self._modem.aldb:
                addr = self._modem.aldb[mem_addr].address.id
                if addr not in address_list and (not self._devices.get(addr) or id_devices == 2):
                    address_list.append(addr)
            await self.id_devices(address_list)

    async def save_devices(self, workdir=''):
        """Save all devices to the `insteon_devices.json` file for faster loading."""
        self._workdir = workdir if workdir else self._workdir
        device_dict = self._device_info_to_dict()
        await self._write_saved_devices(device_dict)

    async def id_devices(self, address_list):
        """Call ID Request command for all unknown devices."""
        from .id_manager import IdManager
        id_manager = IdManager()
        device_info_list = await id_manager.async_id_devices(address_list)
        for address in device_info_list:
            device_id = device_info_list.get(address)
            if device_id.cat:
                device = self._create_device(device_id)
                self._devices[address] = device

    async def _load_saved_devices(self):
        """Add devices from the saved devices or from the device overrides."""
        saved_devices = await self._read_saved_devices()
        for saved_device in saved_devices:
            addr = saved_device.get('address')
            aldb_status = saved_device.get('aldb_status', 0)
            aldb = saved_device.get('aldb', {})
            if not self._devices.get(addr):
                cat = saved_device.get('cat')
                subcat = saved_device.get('subcat')
                firmware = saved_device.get('firmware')
                device_id = DeviceId(addr, cat, subcat, firmware)
                device = self._create_device(device_id)
                if device:
                    device.aldb.load_saved_records(aldb_status, aldb)
                    self._devices[addr] = device
                    _LOGGER.debug('Device with id %s added to device list '
                                  'from saved device data.', addr)
            elif Address(addr) == self._modem.address:
                self._modem.aldb.load_saved_records(aldb_status, aldb)

    def _load_overrides(self):
        for addr in self._overrides:
            if not self._devices.get(addr):
                device_override = self._overrides.get(Address(addr).id, {})
                cat = device_override.get('cat')
                subcat = device_override.get('subcat')
                firmware = device_override.get('firmware')
                device_id = DeviceId(addr, cat, subcat, firmware)
                device = self._create_device(device_id)
                if device:
                    _LOGGER.debug('Device with id %s added to device list '
                                  'from device override data.', addr)
                    self._devices[addr] = device

    def _create_device(self, device_id: DeviceId):
        from ..devices.dummy import DummyDevice
        return DummyDevice(device_id.address, device_id.cat, device_id.subcat,
                           device_id.firmware)

    def _device_info_to_dict(self):
        """Save all device information to the device info file."""
        from ..x10_address import X10Address
        if not self._workdir:
            raise ValueError('Work directory has not been defined yet.')

        devices = []
        for addr in self._devices:
            device = self._devices.get(addr)
            if not isinstance(device.address, X10Address):
                aldb = {}
                for mem in device.aldb:
                    rec = device.aldb[mem]
                    if rec:
                        aldbRec = {'memory': mem,
                                    'control_flags': rec.control_flags.byte,
                                    'group': rec.group,
                                    'address': rec.address.id,
                                    'data1': rec.data1,
                                    'data2': rec.data2,
                                    'data3': rec.data3}
                        aldb[mem] = aldbRec
                deviceInfo = {'address': device.address.id,
                              'cat': device.cat,
                              'subcat': device.subcat,
                              'firmware': device.firmware,
                              'aldb_status': device.aldb.status.value,
                              'aldb': aldb}
                devices.append(deviceInfo)
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
        except FileNotFoundError:
            _LOGGER.error('Cannot write to file %s', device_file)
