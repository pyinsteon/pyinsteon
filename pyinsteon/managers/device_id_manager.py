"""Manage identifying unknown devices."""
import asyncio
from binascii import unhexlify
from collections import namedtuple
import logging

import async_timeout

from .. import pub
from ..address import Address
from ..constants import DeviceAction, ResponseStatus
from ..handlers.all_link_completed import AllLinkCompletedHandler
from ..handlers.from_device.assign_to_all_link_group import AssignToAllLinkGroupCommand
from ..handlers.from_device.delete_from_all_link_group import (
    DeleteFromAllLinkGroupCommand,
)
from ..handlers.to_device.id_request import IdRequestCommand
from ..handlers.to_device.ping import PingCommand
from ..subscriber_base import SubscriberBase
from ..utils import subscribe_topic, unsubscribe_topic

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 5
RETRY_PAUSE = 2
PING_DELAY = 20


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

        # Cannot set queue here because we are outside the loop
        self._awake_devices_queue = None

        self._id_device_lock = asyncio.Lock()
        self._all_link_complete = AllLinkCompletedHandler()
        self._all_link_complete.subscribe(self._all_link_complete_received)
        self._ping_tasks = {}

    def __getitem__(self, address):
        """Return the unknown device list."""
        address = Address(address)
        return self._device_ids.get(address)

    def __setitem__(self, address, device_id):
        """Set a device ID."""
        self._device_ids[address] = device_id

    @property
    def unknown_devices(self):
        """Return a list of addresses where the device type has not been identified."""
        return self._unknown_devices

    def start(self):
        """Start the ID manager for unknown devices."""
        if self._awake_devices_queue is None:
            self._awake_devices_queue = asyncio.Queue()
        asyncio.ensure_future(self._id_awake_devices())

    def close(self):
        """Close the ID listener."""
        if self._awake_devices_queue is not None:
            self._awake_devices_queue.put_nowait(None)
        for _, task in self._ping_tasks.items():
            task.cancel()

    def append(self, address: Address, refresh=False):
        """Append a device address to the list."""
        address = Address(address)

        # If the address is already in the unknown device list stop
        if address in self._unknown_devices and not refresh:
            return

        # If it is not in the identified device list, add it as an unknown device
        device_id = self._device_ids.get(address)
        if refresh or device_id is None or device_id.cat is None:
            self._device_ids[address] = DeviceId(address, None, None, None)
            if address not in self._unknown_devices:
                self._unknown_devices.append(address)
            if address not in self._ping_tasks:
                task = asyncio.ensure_future(self._ping_device(address))
                self._ping_tasks[address] = task
            subscribe_topic(self._device_awake, address.id)

    def set_device_id(
        self,
        address: Address,
        cat: int,
        subcat: int,
        firmware: int = 0x00,
        link_mode=DeviceAction.ADDED,
    ):
        """Set the device ID of a device."""
        address = Address(address)
        cat = _normalize_identifier(cat)
        subcat = _normalize_identifier(subcat)
        firmware = _normalize_identifier(firmware)

        if address in self._unknown_devices:
            self._unknown_devices.remove(address)
        unsubscribe_topic(self._device_awake, address.id)
        if address in self._ping_tasks:
            self._ping_tasks[address].cancel()

        device_id = DeviceId(address, cat, subcat, firmware)
        self._device_ids[address] = device_id
        self._call_subscribers(device_id=device_id, link_mode=link_mode)

    async def async_id_devices(self, refresh: bool = False):
        """Identify the devices in the unknown device list."""
        if refresh:
            for address_id in self._device_ids:
                self.append(address_id, refresh=True)

        # We change the unknown device list during the process so we make a copy
        address_list = self._unknown_devices.copy()
        async with self._id_device_lock:
            for address in address_list:
                await self.async_id_device(address)
        return self._device_ids

    async def async_id_device(self, address: Address, refresh: bool = False):
        """Call ID Request command for all unknown devices."""

        received_queue = asyncio.Queue()

        async def async_device_id_received(device_id, link_mode):
            """Receive notification a device has been identified."""
            await received_queue.put(device_id)

        self.subscribe(async_device_id_received)

        id_handler = IdRequestCommand(address)
        id_response_handler = AssignToAllLinkGroupCommand(address)
        id_response_handler_alt = DeleteFromAllLinkGroupCommand(address)
        id_response_handler.subscribe(self._id_response)
        id_response_handler_alt.subscribe(self._id_response)

        address = Address(address)
        device_id = DeviceId(address, None, None, None)
        self.append(address, refresh)

        retries = MAX_RETRIES
        try:
            while retries:
                response = await id_handler.async_send()
                if response == ResponseStatus.SUCCESS:
                    try:
                        async with async_timeout.timeout(RETRY_PAUSE):
                            return await received_queue.get()
                    except asyncio.TimeoutError:
                        pass
                elif response in [
                    ResponseStatus.DIRECT_NAK_ALDB,
                    ResponseStatus.DIRECT_NAK_CHECK_SUM,
                    ResponseStatus.DIRECT_NAK_INVALID_COMMAND,
                ]:
                    _LOGGER.warning(
                        "Device %s refused the Device ID request with error: %s (%r)",
                        str(address),
                        str(response),
                        response,
                    )
                    return None

                retries -= 1
                await asyncio.sleep(RETRY_PAUSE)

        finally:
            id_response_handler.unsubscribe(self._id_response)
            id_response_handler_alt.unsubscribe(self._id_response)

        return device_id

    def _id_response(self, address, cat, subcat, firmware, group, link_mode):
        """Receive a device ID response."""
        self.set_device_id(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=firmware,
            link_mode=link_mode,
        )

    async def _id_awake_devices(self):
        """Loop on devices that wake up and send a message."""
        if self._awake_devices_queue is None:
            self._awake_devices_queue = asyncio.Queue()
        while True:
            address = await self._awake_devices_queue.get()
            if address is None:
                break
            await asyncio.sleep(0.5)
            device_id = await self.async_id_device(address=address)
            if device_id and device_id.cat is None:
                subscribe_topic(self._device_awake, address.id)
            elif device_id is None:
                unsubscribe_topic(self._device_awake, address.id)
                if address in self._ping_tasks:
                    self._ping_tasks[address].cancel()
                break

    def _device_awake(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Identify an unknown device.

        An unknown device has sent a message so we try to identify it.

        """
        # If the async_id_devices method is running do not proceed
        if self._id_device_lock.locked():
            return

        try:
            address = Address(topic.name.split(".")[0])
        except ValueError:
            return

        unsubscribe_topic(self._device_awake, address.id)

        # Has the device been identified already
        device_id = self._device_ids.get(address)
        if device_id and device_id.cat is not None:
            return

        if self._awake_devices_queue is None:
            self._awake_devices_queue = asyncio.Queue()
        self._awake_devices_queue.put_nowait(address)

    def _all_link_complete_received(
        self, link_mode, group, target, cat, subcat, firmware
    ):
        """Receive All-Link complete message."""
        self._id_response(target, cat, subcat, firmware, group, link_mode)

    async def _ping_device(self, address):
        """Ping the device until awake."""
        cmd = PingCommand(address)
        response = None
        retry_wait = 60
        retries = (
            24 * 60 * 1.5
        )  # 1.5 days. If a devices does not respond in this time it is dead
        try:
            while retries and response != ResponseStatus.SUCCESS:
                device_id = self._device_ids.get(address)
                if device_id is not None and device_id.cat is not None:
                    return
                await asyncio.sleep(retry_wait)
                response = await cmd.async_send()
                if response in [
                    ResponseStatus.DIRECT_NAK_ALDB,
                    ResponseStatus.DIRECT_NAK_CHECK_SUM,
                    ResponseStatus.DIRECT_NAK_INVALID_COMMAND,
                    ResponseStatus.DIRECT_NAK_NO_LOAD,
                ]:
                    _LOGGER.warning(
                        "Device %s rejected an ID request with error: %s (%r)",
                        str(address),
                        response,
                        response,
                    )
                    return
                retries -= 1
        except asyncio.CancelledError:
            return
