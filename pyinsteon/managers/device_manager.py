"""Device manager."""
import logging
import asyncio

from ..address import Address
from ..x10_address import X10Address
from ..device_types.device_base import Device
from ..device_types.x10_base import X10DeviceBase
from ..device_types.modem_base import ModemBase
from ..managers.saved_devices_manager import SavedDeviceManager
from ..subscriber_base import SubscriberBase
from .device_id_manager import DeviceId, DeviceIdManager
from .device_link_manager import DeviceLinkManager
from .utils import create_device, create_x10_device

DEVICE_INFO_FILE = "insteon_devices.json"
_LOGGER = logging.getLogger(__name__)


# TODO remove devices
class DeviceManager(SubscriberBase):
    """Manages the list of active devices."""

    def __init__(self):
        """Init the DeviceManager class."""
        super().__init__(subscriber_topic="device_added")
        self._devices = {}
        self._modem = None
        self._id_manager = DeviceIdManager()
        self._id_manager.subscribe(self._device_identified)
        self._loading_saved_lock = asyncio.Lock()
        self._link_manager = DeviceLinkManager(self)

    def __getitem__(self, address) -> Device:
        """Return a a device from the device address."""
        try:
            address = Address(address)
        except ValueError:
            address = X10Address(address)
        return self._devices.get(address)

    def __iter__(self):
        """Return an iterator of device addresses."""
        for address in self._devices:
            yield address

    def __setitem__(self, address, device):
        """Add a device to the device list."""
        _LOGGER.info("Adding device to INSTEON devices list: %s", address.id)
        if not isinstance(device, (Device, DeviceId, X10DeviceBase)):
            raise ValueError("Device must be a DeviceId or a Device type.")

        if isinstance(device, DeviceId):
            device = create_device(device)

        self._devices[device.address] = device
        if isinstance(device, Device):
            self._id_manager.set_device_id(
                device.address, device.cat, device.subcat, device.firmware
            )
        self._call_subscribers(address=device.address.id)

    def __len__(self):
        """Return the number of devices."""
        return len(self._devices)

    def get(self, address) -> Device:
        """Return a device from an address."""
        try:
            address = Address(address)
        except ValueError:
            address = X10Address(address)
        return self._devices.get(address)

    def pop(self, address):
        """Remove a device from the device list."""
        try:
            address = Address(Address)
        except ValueError:
            address = X10Address(address)
        self._devices.pop(address)

    @property
    def modem(self):
        """Return the Insteon Modem."""
        return self._modem

    @modem.setter
    def modem(self, modem):
        """Set the Insteon Modem."""
        if not isinstance(modem, ModemBase):
            raise ValueError("Must be an Insteon Modem object")
        self._modem = modem
        self._devices[self._modem.address] = self._modem

    @property
    def id_manager(self):
        """Return the ID manager instance."""
        return self._id_manager

    def set_id(self, address: Address, cat: int, subcat: int, firmware: int):
        """Add a device override to identify the device information.

        Typical use is to identify devices that do not respond to an ID Request
        such as a battery opperated device.

        """
        address = Address(address)
        device = self[address]
        if device and device.cat == cat and device.subcat == subcat:
            return
        self._id_manager.set_device_id(address, cat, subcat, firmware)

    async def async_identify_device(self, address: Address):
        """Identify a device.

        The device will be placed into the unknown device list to be identified.

        If the device has already been identified, this method will remove the device
        from the known device list. This is typically used when a `set_id` command has
        been run to create a device override. The `async_reidentify_device` command will
        reset that override and allow normal device identification to run.
        """
        self._devices.pop(Address(address))
        await self._id_manager.async_id_device(address=address, refresh=True)

    def add_x10_device(
        self,
        housecode: str,
        unitcode: int,
        x10_feature: str,
        steps: int = 22,
        max_level: int = 255,
    ):
        """Add an X10 device."""
        device = create_x10_device(housecode, unitcode, x10_feature, steps, max_level)
        if device:
            self[device.address] = device
        return device

    async def async_close(self):
        """Close the device ID listener."""
        self._id_manager.close()

    async def async_load(self, workdir="", id_devices=1, load_modem_aldb=1):
        """Load devices from the `insteon_devices.yaml` file and device overrides.

        Parameters:
            workdir: Directory name to find the `insteon_devices.json` file

            id_devices: Indicate if devices should be identified using ID Request
                0: No devices are identified
                1: Unknown devices are identified
                2: All devices are identified
            (default=1)

            load_modem_aldb: Indicate if the Modem ALDB should be loaded
                0: Do not load
                1: Load if not loaded from save file
                2: Load
            (default=1)

        The Modem ALDB is loaded if `refresh` is True or if the saved file has no devices.

        """
        if workdir:
            async with self._loading_saved_lock:
                saved_devices_manager = SavedDeviceManager(workdir, self.modem)
                devices = await saved_devices_manager.async_load()
                for address in devices:
                    self[address] = devices[address]

        if load_modem_aldb == 0:
            load_modem_aldb = False
        elif load_modem_aldb == 2:
            load_modem_aldb = True
        else:
            load_modem_aldb = not self._modem.aldb.is_loaded

        if load_modem_aldb:
            await self._modem.aldb.async_load()

        for mem_addr in self._modem.aldb:
            rec = self._modem.aldb[mem_addr]
            if rec.target != Address("000000"):
                self._id_manager.append(rec.target)

        if id_devices:
            id_all = id_devices == 2
            await self._id_manager.async_id_devices(refresh=id_all)

    async def async_save(self, workdir):
        """Save devices to a device information file."""
        saved_devices_manager = SavedDeviceManager(workdir, self.modem)
        await saved_devices_manager.async_save(self._devices)

    def _device_identified(self, device_id: DeviceId):
        """Device identified by device ID manager."""
        if self._loading_saved_lock.locked():
            return
        if device_id.cat is not None:
            device = create_device(device_id)
            if self[device_id.address]:
                # If the device is already in the devices list and the cat and subcat
                # are the same, do not add the device again
                if (
                    device_id.cat == self[device_id.address].cat
                    and device_id.subcat == self._devices[device_id.address].subcat
                ):
                    return
            self[device_id.address] = device
            if device_id.cat != 0x03:
                asyncio.ensure_future(device.async_get_engine_version())
                asyncio.ensure_future(self.async_setup_device(device))
            _LOGGER.debug("Device %s added", device.address)

    async def async_setup_device(self, device):
        """Set up device."""
        await device.aldb.async_load(refresh=True)
        await device.async_read_op_flags()
        await device.async_read_ext_properties()
        await device.async_add_default_links()
