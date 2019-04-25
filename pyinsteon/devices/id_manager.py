"""Device ID manager."""
from asyncio import sleep
from collections import namedtuple

from ..address import Address
from ..handlers.id_request import IdRequestCommand

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
            id_handler.subscribe(self._id_response)
            retries = 0
            while self._address_list[addr].cat is None and retries <= 5:
                await id_handler.async_send()
                retries += 1
                await sleep(1)
            id_handler.unsubscribe(self._id_response)
        return self._address_list

    def _id_response(self, address, cat, subcat, firmware):
        address = Address(address)
        self._address_list[address.id] = DeviceId(address, cat, subcat, firmware)
