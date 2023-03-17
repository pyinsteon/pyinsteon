"""Extended property read manager."""
import asyncio

import async_timeout

from ..address import Address
from ..constants import ResponseStatus
from ..handlers.from_device.ext_get_response import ExtendedGetResponseHandler
from ..handlers.to_device.extended_get import ExtendedGetCommand
from ..subscriber_base import SubscriberBase

RETRIES = 3
WAIT_RESPONSE = 5


class ExtenededGetManager(SubscriberBase):
    """Extended get command manager."""

    def __init__(
        self,
        address: Address,
        cmd2: int = 0,
        data1_read: int = 0x00,
        data2_read: int = 0x00,
        data3_read: int = None,
        data1_resp: int = 0x00,
        data2_resp: int = 0x01,
        data3_resp: int = None,
    ):
        """Init the ExtenededPropertyReadManager class."""
        self._address = Address(address)
        self._data1_read = data1_read
        self._read_command = ExtendedGetCommand(
            self._address,
            cmd2=cmd2,
            data1=data1_read,
            data2=data2_read,
            data3=data3_read,
        )
        self._response = ExtendedGetResponseHandler(
            self._address,
            cmd2=cmd2,
            data1=data1_resp,
            data2=data2_resp,
            data3=data3_resp,
        )

        response_group = str(cmd2)
        for data in (data1_read, data2_read, data3_read):
            response_group = f"{response_group}.{data if data is not None else '_'}"
        super().__init__(
            f"{self._address.id}.extended_read_manager.{response_group}.response"
        )
        self._response.subscribe(self._response_received)
        self._response_queue = asyncio.Queue()

    async def async_send(self):
        """Send the GET command."""
        retries = RETRIES
        while retries:
            response = await self._read_command.async_send(group=self._data1_read)
            if response == ResponseStatus.SUCCESS:
                response = ResponseStatus.DEVICE_UNRESPONSIVE
                try:
                    async with async_timeout.timeout(WAIT_RESPONSE):
                        return await self._response_queue.get()
                except asyncio.TimeoutError:
                    pass
            retries -= 1
        return response

    async def _response_received(self, group, data):
        """Response received."""
        self._call_subscribers(group=group, data=data)
        await self._response_queue.put(ResponseStatus.SUCCESS)
