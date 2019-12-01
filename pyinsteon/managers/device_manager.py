"""Device manager."""
from asyncio import Lock
import logging

from ..subscriber_base import SubscriberBase
from ..device_types import Device
from ..address import Address
from ..managers.device_id_manager import DeviceIdManager, DeviceId

DEVICE_INFO_FILE = 'insteon_devices.json'
_LOGGER = logging.getLogger(__name__)


def create_device(device_id: DeviceId):
    """Create an Insteon Device from a DeviceId named Tuple."""
    from ..device_types.ipdb import IPDB
    ipdb = IPDB()
    product = ipdb[[device_id.cat, device_id.subcat]]
    deviceclass = product.deviceclass
    device = None
    if deviceclass is not None:
        device = deviceclass(device_id.address,
                             device_id.cat,
                             device_id.subcat,
                             device_id.firmware,
                             product.description,
                             product.model)
    return device


class DeviceManager(SubscriberBase):
    """Manages the list of active devices."""

    def __init__(self):
        """Init the DeviceManager class."""
        super().__init__(subscriber_topic='device_added')
        self._devices = {}
        self._modem = None
        self._id_manager = DeviceIdManager()
        self._id_manager.subscribe(self._device_identified)
        self._loading_saved_lock = Lock()

    def __getitem__(self, address) -> Device:
        """Return a a device from the device address."""
        address = Address(address)
        return self._devices.get(address)

    def __iter__(self):
        """Return an iterator of device addresses."""
        for address in self._devices:
            yield address

    def __setitem__(self, address, device):
        """Add a device to the device list."""
        if not isinstance(device, (Device, DeviceId)):
            raise ValueError('Device must be a DeviceId or a Device type.')

        if isinstance(device, DeviceId):
            device = create_device(device)

        self._devices[device.address] = device
        self._id_manager.set_device_id(device.address, device.cat,
                                       device.subcat, device.firmware)
        self._call_subscribers(address=device.address)

    def __len__(self):
        """Return the number of devices."""
        return len(self._devices)

    def get(self, address) -> Device:
        """Return a device from an address."""
        address = Address(address)
        return self._devices.get(address)

    @property
    def modem(self):
        """Return the Insteon Modem."""
        return self._modem

    @modem.setter
    def modem(self, modem):
        """Set the Insteon Modem."""
        from ..device_types.modem_base import ModemBase
        if not isinstance(modem, ModemBase):
            raise ValueError('Must be an Insteon Modem object')
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
        self._id_manager.set_device_id(address, cat, subcat, firmware)

    async def async_close(self):
        """Close the device ID listener."""
        self._id_manager.close()

    async def async_load(self, workdir='', id_devices=1, refresh=False):
        """Load devices from the `insteon_devices.yaml` file and device overrides.

        Parameters:
            workdir: Directory name to find the `insteon_devices.json` file

            id_devices: Indicate if devices should be identified using ID Request
                0: No devices are identified
                1: Unknown devices are identified
                2: All devices are identified
            (default=1)

            refresh: Bool to indicate if the Modem ALDB should be reloaded to identify
            new devices (Default=False)

        The Modem ALDB is loaded if `refresh` is True or if the saved file has no devices.
        """
        from ..managers.saved_devices_manager import SavedDeviceManager
        if workdir:
            await self._loading_saved_lock.acquire()
            saved_devices_manager = SavedDeviceManager(workdir)
            devices = await saved_devices_manager.async_load()
            for address in devices:
                self[address] = devices[address]
            if self._loading_saved_lock.locked():
                self._loading_saved_lock.release()

        if ((len(self._devices) == 1 and not self._modem.aldb.is_loaded) or
                refresh):
            # No devices were found in the saved devices file or reload_aldb is required
            await self._modem.aldb.async_load()

        for mem_addr in self._modem.aldb:
            rec = self._modem.aldb[mem_addr]
            if rec.target != Address('000000'):
                self._id_manager.append(rec.target)

        if id_devices:
            id_all = id_devices == 2
            await self._id_manager.async_id_devices(refresh=id_all)

    async def async_save(self, workdir):
        """Save devices to a device information file."""
        from ..managers.saved_devices_manager import SavedDeviceManager
        saved_devices_manager = SavedDeviceManager(workdir)
        await saved_devices_manager.async_save(self._devices)

    def _device_identified(self, device_id: DeviceId):
        """Device identified by device ID manager."""
        if self._loading_saved_lock.locked():
            return
        if device_id.cat is not None:
            device = create_device(device_id)
            self[device_id.address] = device
            _LOGGER.debug('Device %s added', device.address)
