"""Device ID manager."""
from asyncio import sleep
from collections import namedtuple

from ..address import Address
from ..handlers.to_device.id_request import IdRequestCommand
from ..handlers.from_device.assign_to_all_link_group import AssignToAllLinkGroupCommand

DeviceId = namedtuple('DeviceId', 'address cat subcat firmware')

class IdManager:
    """Manage the device ID process."""

    def __init__(self):
        """Init the IdManager class."""
        self._address_list = {}
        self._current_device_id = DeviceId(None, None, None, None)

    def __getitem__(self, address):
        """Get the device info from the device address list."""
        address_id = Address(address).id
        return self._address_list.get(address_id)

    async def async_id_devices(self, address_list, force_reload=False):
        """Identify the devices in the modem All-Link Database."""
        for address in address_list:
            address_id = Address(address).id
            self._address_list[address_id] = DeviceId(None, None, None, None)
        for addr in address_list:
            id_handler = IdRequestCommand(addr)
            id_response_handler = AssignToAllLinkGroupCommand(addr)
            id_response_handler.subscribe(self._id_response)
            retries = 0
            while self._address_list[addr].cat is None and retries <= 5:
                await id_handler.async_send()
                retries += 1
                await sleep(1)
            id_response_handler.unsubscribe(self._id_response)
        return self._address_list

    def _id_response(self, address, cat, subcat, firmware, group, mode):
        address = Address(address)
        device = DeviceId(address, cat, subcat, firmware)
        if device:
            self._address_list[address.id] = device
