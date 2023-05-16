"""Extended property read manager."""
from typing import Dict

from ..address import Address
from ..config.extended_property import ExtendedProperty
from ..constants import ResponseStatus
from .ext_get_manager import ExtenededGetManager


class ExtendedPropertyReadManager(ExtenededGetManager):
    """Extended property read manager."""

    def __init__(
        self,
        address: Address,
        properties: Dict[int, ExtendedProperty],
        cmd2: int = 0,
        data1_read: int = 0x00,
        data2_read: int = 0x00,
        data3_read: int = None,
        data1_resp: int = 0x00,
        data2_resp: int = 0x01,
        data3_resp: int = None,
    ):
        """Init the ExtendedPropertyReadManager class."""
        super().__init__(
            address=address,
            cmd2=cmd2,
            data1_read=data1_read,
            data2_read=data2_read,
            data3_read=data3_read,
            data1_resp=data1_resp,
            data2_resp=data2_resp,
            data3_resp=data3_resp,
        )
        self._props: Dict[int, ExtendedProperty] = properties

    async def _response_received(self, group, data):
        """Update properties based on the extended get response."""
        for index, prop in self._props.items():
            prop.set_value(data[f"data{index}"])
        await self._response_queue.put(ResponseStatus.SUCCESS)
