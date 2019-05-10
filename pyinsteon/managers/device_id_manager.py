"""Manage identifying unknown devices."""
import asyncio
from collections import namedtuple
import logging

from .. import pub
from ..subscriber_base import SubscriberBase
from ..address import Address
from ..handlers.to_device.id_request import IdRequestCommand
from ..handlers.from_device.assign_to_all_link_group import AssignToAllLinkGroupCommand

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 5
RETRY_PAUSE = 2


DeviceId = namedtuple('DeviceId', 'address cat subcat firmware')


class DeviceIdManager(SubscriberBase):
    """Manage device identities."""

    def __init__(self):
        """Init the DeviceIdManager class."""
        super().__init__()
        self._unknown_devices = []
        self._device_ids = {}
        self._awake_devices = []
        self._awake_devices_queue = asyncio.Queue()
        self._id_device_lock = asyncio.Lock()
        asyncio.ensure_future(self._id_awake_devices())

    def __getitem__(self, address):
        """Return the unknown device list."""
        address = Address(address)
        device_id = self._device_ids.get(address)
        if not device_id:
            self.append(address)

    def close(self):
        """Close the ID listener."""
        self._awake_devices_queue.put_nowait(None)

    def append(self, address: Address):
        """Append a device address to the list."""
        address = Address(address)
        # If the address is already in the unknown device list stop
        if address in self._unknown_devices:
            return

        # If it is not in the identified device list, add it as an unknown device
        if self._device_ids.get(address) is None:
            self._device_ids[address] = DeviceId(None, None, None, None)
            self._unknown_devices.append(address)
            pub.subscribe(self._device_awake, address.id)

    def set_device_id(self, address: Address, cat: int, subcat: int, firmware: int = 0x00):
        """Set the device ID of a device."""
        address = Address(address)
        cat = int(cat)
        subcat = int(subcat)
        firmware = int(firmware)
        try:
            self._unknown_devices.remove(address)
        except ValueError:
            pass
        device_id = DeviceId(address, cat, subcat, firmware)
        self._device_ids[address] = device_id
        self._call_subscribers(device_id=device_id)

    async def async_id_devices(self, refresh: bool = False):
        """Identify the devices in the unknown device list."""
        if refresh:
            for address_id in self._device_ids:
                self._device_ids[address_id] = DeviceId(None, None, None, None)
                address = Address(address_id)
                if address not in self._unknown_devices:
                    self._unknown_devices.append(address)
        # We change the unknown device list during the process so we make a copy
        address_list = self._unknown_devices.copy()
        for address in address_list:
            await self.async_id_device(address)
        return self._device_ids

    async def async_id_device(self, address: Address, refresh: bool = False):
        """Call ID Request command for all unknown devices"""
        if self._id_device_lock.locked():
            self._id_device_lock.release()
        await self._id_device_lock.acquire()
        address = Address(address)
        self.append(address)
        if refresh:
            self._device_ids = DeviceId(None, None, None, None)
        id_handler = IdRequestCommand(address)
        id_response_handler = AssignToAllLinkGroupCommand(address)
        id_response_handler.subscribe(self._id_response)
        retries = 0
        while self._device_ids[address].cat is None and retries <= MAX_RETRIES:
            await id_handler.async_send()
            retries += 1
            await asyncio.sleep(RETRY_PAUSE)
        id_response_handler.unsubscribe(self._id_response)
        if self._id_device_lock.locked():
            self._id_device_lock.release()
        return self._device_ids[address]

    def _id_response(self, address, cat, subcat, firmware, group, mode):
        address = Address(address)
        device_id = DeviceId(address, cat, subcat, firmware)
        self._device_ids[address] = device_id
        try:
            self._unknown_devices.remove(address)
        except ValueError:
            pass
        self._call_subscribers(device_id=device_id)

    async def _id_awake_devices(self):
        """Loop on devices that wake up and send a message."""
        while True:
            address = await self._awake_devices_queue.get()
            if address is None:
                break
            await self.async_id_device(address=address)
            await asyncio.sleep(2)
            self._check_awake_device(address)

    def _check_awake_device(self, address):
        """Check if an awake device has been identified."""
        if not self._device_ids.get(address):
            pub.subscribe(self._device_awake, address.id)
        try:
            self._awake_devices.remove(address)
        except ValueError:
            pass

    def _device_awake(self, topic=pub.AUTO_TOPIC, **kwargs):
        """An unknown device has sent a message so we try to identify it."""
        try:
            address = Address(topic.name.split('.')[0])
        except ValueError:
            pass
        else:
            if address in self._awake_devices:
                return
            pub.unsubscribe(self._device_awake, address.id)
            self._awake_devices.append(address)
            self._awake_devices_queue.put_nowait(address)
