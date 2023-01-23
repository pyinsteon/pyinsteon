"""Device manager."""
import asyncio
import logging

import async_timeout

from ..address import Address
from ..constants import AllLinkMode, DeviceAction
from ..device_types.device_base import Device
from ..device_types.modem_base import ModemBase
from ..device_types.x10_base import X10DeviceBase
from ..managers.saved_devices_manager import SavedDeviceManager
from ..subscriber_base import SubscriberBase
from ..topics import DEVICE_LIST_CHANGED
from ..x10_address import X10Address
from .device_id_manager import DeviceId, DeviceIdManager
from .link_manager import (
    async_cancel_linking_mode,
    async_enter_linking_mode,
    async_enter_unlinking_mode,
    async_unlink_devices,
)
from .utils import create_device, create_x10_device

DEVICE_INFO_FILE = "insteon_devices.json"
_LOGGER = logging.getLogger(__name__)
_DEVICE_LOGGERS = []


class DeviceManager(SubscriberBase):
    """Manages the list of active devices."""

    def __init__(self):
        """Init the DeviceManager class."""
        super().__init__(subscriber_topic=DEVICE_LIST_CHANGED)
        self._devices = {}
        self._modem = None
        self._id_manager = DeviceIdManager()
        self._id_manager.subscribe(self._async_device_identified)
        self._loading_saved_lock = asyncio.Lock()

        self._delay_device_inspection = False
        self._to_be_inspected = []
        self._linked_device = asyncio.Queue()

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
        if device is None:
            _LOGGER.info("Removing device from INSTEON devices list: %s", address.id)
            if address in self._devices:
                self._devices.pop(address)
                self._call_subscribers(address=address.id, action=DeviceAction.REMOVED)
            return

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
        self._call_subscribers(address=device.address.id, action=DeviceAction.ADDED)

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

    @property
    def delay_inspection(self):
        """Return the status of device inspection after identification.

        When a new device is identified the Device Manager will inspect the device
        for its operating flags, extended properties and All-Link Database automatically
        by default. Setting this property to `False` will delay device inspection until
        `inspect_devices` is called.

        """
        return self._delay_device_inspection

    @delay_inspection.setter
    def delay_inspection(self, value):
        """Set the delay inspection property."""
        self._delay_device_inspection = bool(value)

    @property
    def unknown_devices(self):
        """Return a list of addresses where the device type is unknown."""
        return self._id_manager.unknown_devices

    async def async_inspect_devices(self):
        """Inspect the properties of the devices who's inspection was delayed ealier."""
        while self._to_be_inspected:
            device = self._to_be_inspected.pop()
            await device.async_read_config()

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

    async def async_add_device(self, address: Address = None, multiple: bool = False):
        """Add one or more devices.

        This command will place the modem in linking mode.

        If an address is entered, it will attempt to place that device in linking mode.

        If multiple is True, the command will continue to place the modem in linking mode until
        the `async_cancel_add_device` command is executed.

        This command can be canceled at any time with the `async_cancel_add_device` command.
        """

        if address is not None:
            address = Address(address)

        self._delay_device_inspection = multiple
        link_next = True
        while not self._linked_device.empty():
            self._linked_device.get_nowait()
        try:
            while link_next:
                await async_enter_linking_mode(
                    link_mode=AllLinkMode.EITHER, group=0, address=address
                )
                # Make sure we don't try to put the same address in linking mode again if multiple is True
                address = None
                async with async_timeout.timeout(3 * 60):
                    linked_address = await self._linked_device.get()
                    link_next = multiple and linked_address
                    yield linked_address
        except asyncio.TimeoutError:
            pass
        finally:
            await async_cancel_linking_mode()
            self._call_subscribers(address=None, action=DeviceAction.COMPLETED)
            if self._delay_device_inspection:
                self._delay_device_inspection = False
                asyncio.ensure_future(self.async_inspect_devices())

    async def async_remove_device(self, address: Address = None, force: bool = False):
        """Remove one or more devices.

        This method will remove all links in the modem were the device is the target and
        all links in the device where the modem is the target.

        If `force` is `True` this method will not attempt to place the device in unlinking mode.
        Therefore the device database will not be changed. All modem links to the device will be removed.
        """
        if address is not None:
            address = Address(address)

        while not self._linked_device.empty():
            self._linked_device.get_nowait()
        try:
            await async_enter_unlinking_mode(group=0, address=address)
            async with async_timeout.timeout(3 * 60):
                unlinked_address = await self._linked_device.get()
                if unlinked_address:
                    await async_unlink_devices(self.modem, unlinked_address)
                    return unlinked_address
                return None
        finally:
            await async_cancel_linking_mode()

    async def async_cancel_all_linking(self):
        """Cancel the All-Link process.

        This command takes the modem out of linking mode.
        """
        await self._linked_device.put(False)

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
            if rec.is_in_use and rec.target != Address("000000"):
                self._id_manager.append(rec.target)

        if id_devices:
            id_all = id_devices == 2
            await self._id_manager.async_id_devices(refresh=id_all)

    async def async_save(self, workdir):
        """Save devices to a device information file."""
        saved_devices_manager = SavedDeviceManager(workdir, self.modem)
        await saved_devices_manager.async_save(self._devices)

    async def _async_device_identified(
        self, device_id: DeviceId, link_mode: AllLinkMode
    ):
        """Device identified by device ID manager."""
        if self._loading_saved_lock.locked():
            return

        await self._linked_device.put(device_id.address)
        device = self._devices.get(device_id.address)
        if (
            device
            and device.cat == device_id.cat
            and device.subcat == device_id.subcat
            and device.firmware == device_id.firmware
        ):
            return

        if link_mode == AllLinkMode.DELETE:
            _LOGGER.debug("Device %s removed", str(device_id.address))
            self[device_id.address] = None
            return

        if device_id.cat is not None:  # How could this be None?
            if (
                self[device_id.address]
                and device_id.cat == self[device_id.address].cat
                and device_id.subcat == self._devices[device_id.address].subcat
            ):
                return

            device = create_device(device_id)
            self[device_id.address] = device
            if device_id.cat != 0x03:
                if self._delay_device_inspection:
                    self._to_be_inspected.append(device)
                else:
                    await device.async_read_config()
            _LOGGER.debug("Device %s added", str(device.address))
            _DEVICE_LOGGERS.append(
                logging.getLogger(f"pyinsteon.{device_id.address.id}")
            )

    async def _async_remove_all_device_links(self, address: Address):
        """Remove all ALDB records from the device to the modem.

        This does not remove the modem as a controller to group 0.
        That is removed via All-Linking.
        """
        if self._devices.get(address) is None:
            return
        for rec in self[address].aldb.find(target=self.modem.address, in_use=True):
            if rec.group != 0 or rec.is_controller:  # do not process group 0 responder
                self[address].aldb.modify(mem_addr=rec.mem_addr, in_use=False)
        await self[address].aldb.async_write()
