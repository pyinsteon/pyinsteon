"""Extended Get property manager."""
import asyncio
from ..address import Address
from ..subscriber_base import SubscriberBase
from ..handlers.to_device.extended_get import ExtendedGetCommand
from ..handlers.from_device.ext_get_response import ExtGetResponseHandler
from ..handlers import ResponseStatus

TIMEOUT = 5

class ExtendedGetManager(SubscriberBase):
    """Extended Get manager."""

    def __init__(self, address):
        """Init the ExtendedGetManager class."""
        super().__init__()
        self._address = Address(address)
        self._get_command = ExtendedGetCommand(self._address)
        self._response_handler = ExtGetResponseHandler(self._address)
        self._response_handler.subscribe(self._receive_response)
        self._response_queue = asyncio.Queue()

    async def async_send(self, button=0):
        """Get the extended properties of the device."""
        while not self._response_queue.empty():
            await self._response_queue.get()
        response = await self._get_command.async_send(button)
        print('Got response:', response)
        if response == ResponseStatus.SUCCESS:
            try:
                properties = await asyncio.wait_for(self._response_queue.get(), TIMEOUT)
            except asyncio.TimeoutError:
                pass
            else:
                print('Setting the properties')
                self._call_subscribers(properties=properties)
                return ResponseStatus.SUCCESS
        print('getting properties failed')
        return ResponseStatus.FAILURE

    def _receive_response(self, data):
        """Handle the response from the device."""
        self._response_queue.put_nowait(data)
