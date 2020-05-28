"""Manage identifying unknown devices."""
import asyncio
import logging
from collections import namedtuple

from binascii import unhexlify

from .. import pub
from ..utils import subscribe_topic, unsubscribe_topic
from ..address import Address
from ..handlers.from_device.assign_to_all_link_group import AssignToAllLinkGroupCommand
from ..handlers.all_link_completed import AllLinkCompletedHandler
from ..handlers.from_device.delete_from_all_link_group import (
    DeleteFromAllLinkGroupCommand,
)
from ..handlers.to_device.id_request import IdRequestCommand
from ..subscriber_base import SubscriberBase

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 5
RETRY_PAUSE = 2


DeviceId = namedtuple("DeviceId", "address cat subcat firmware")  # product_id')


def _normalize_identifier(value):
    """Convert a byte, str or int to int."""
    if value is None:
        return value
    if isinstance(value, (bytearray, bytes)):
        return int.from_bytes(value, "big")
    if isinstance(value, str):
        if value[0:2] == "0x":
            value = value[2:]
        return int.from_bytes(unhexlify(value), "big")
    return int(value)


class DeviceIdManager(SubscriberBase):
    """Manage device identities."""

    def __init__(self):
        """Init the DeviceIdManager class."""
        super().__init__(subscriber_topic="device_id")
        self._unknown_devices = []
        self._device_ids = {}
        self._awake_devices = []
        # Cannot set queue here because we are outside the loop
        self._awake_devices_queue = None
        self._id_device_lock = asyncio.Lock()
        self._all_link_complete = AllLinkCompletedHandler()
        self._all_link_complete.subscribe(self._all_link_complete_received)

    def __getitem__(self, address):
        """Return the unknown device list."""
        address = Address(address)
        return self._device_ids.get(address)

    def start(self):
        """Start the ID manager for unknown devices."""
        asyncio.ensure_future(self._id_awake_devices())

    def close(self):
        """Close the ID listener."""
        if self._awake_devices_queue is not None:
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
            subscribe_topic(self._device_awake, address.id)

    def set_device_id(
        self, address: Address, cat: int, subcat: int, firmware: int = 0x00
    ):
        """Set the device ID of a device."""
        address = Address(address)
        cat = _normalize_identifier(cat)
        subcat = _normalize_identifier(subcat)
        firmware = _normalize_identifier(firmware)
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
        """Call ID Request command for all unknown devices."""
        if self._id_device_lock.locked():
            self._id_device_lock.release()
        await self._id_device_lock.acquire()
        address = Address(address)
        self.append(address)
        if refresh:
            self._device_ids[address] = DeviceId(None, None, None, None)
        id_handler = IdRequestCommand(address)
        id_response_handler = AssignToAllLinkGroupCommand(address)
        id_response_handler.subscribe(self._id_response)
        id_response_handler_alt = DeleteFromAllLinkGroupCommand(address)
        id_response_handler_alt.subscribe(self._id_response)
        retries = 0
        while self._device_ids[address].cat is None and retries <= MAX_RETRIES:
            # TODO check for success or failure
            await id_handler.async_send()
            retries += 1
            await asyncio.sleep(RETRY_PAUSE)
        id_response_handler.unsubscribe(self._id_response)
        id_response_handler_alt.unsubscribe(self._id_response)
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
        unsubscribe_topic(self._device_awake, address.id)
        self._call_subscribers(device_id=device_id)

    def _set_device_info(
        self, address, cat=None, subcat=None, firmware=None, product_id=None
    ):
        """Set the device ID info."""
        device_id = self._device_ids.get(address)
        if device_id is None:
            new_id = DeviceId(address, cat, subcat, firmware)
        else:
            new_id = DeviceId(
                address,
                cat if cat else device_id.cat,
                subcat if subcat else device_id.subcat,
                firmware if firmware else device_id.firmware,
            )
        self._device_ids[address] = new_id

    async def _id_awake_devices(self):
        """Loop on devices that wake up and send a message."""
        if self._awake_devices_queue is None:
            self._awake_devices_queue = asyncio.Queue()
        while True:
            address = await self._awake_devices_queue.get()
            if address is None:
                break
            await asyncio.sleep(0.5)
            await self.async_id_device(address=address)
            await asyncio.sleep(2)
            self._check_awake_device(address)

    def _check_awake_device(self, address):
        """Check if an awake device has been identified."""
        dev_id = self._device_ids.get(address)
        if dev_id is None or dev_id.cat is None:
            subscribe_topic(self._device_awake, address.id)
        try:
            self._awake_devices.remove(address)
        except ValueError:
            pass

    def _device_awake(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Identify an unknown device.

        An unknown device has sent a message so we try to identify it.

        """
        if self._id_device_lock.locked():
            return
        try:
            address = Address(topic.name.split(".")[0])
        except ValueError:
            pass
        else:
            if address in self._awake_devices:
                return
            unsubscribe_topic(self._device_awake, address.id)
            self._awake_devices.append(address)
            if self._awake_devices_queue is None:
                self._awake_devices_queue = asyncio.Queue()
            self._awake_devices_queue.put_nowait(address)

    def _all_link_complete_received(self, mode, group, target, cat, subcat, firmware):
        """Receive All-Link complete message."""
        self._id_response(target, cat, subcat, firmware, group, mode)
