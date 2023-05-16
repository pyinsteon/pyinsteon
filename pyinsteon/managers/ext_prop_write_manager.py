"""Extended property set manager."""

from typing import Dict

from ..address import Address
from ..config.extended_property import ExtendedProperty
from ..constants import ResponseStatus
from ..handlers.to_device.extended_set import ExtendedSetCommand

RETRIES = 3


def _value(prop: ExtendedProperty):
    """Return the usable value from a property."""
    return prop.new_value if prop.is_dirty else prop.value


class ExtendedPropertyWriteManager:
    """Extended property read manager."""

    def __init__(
        self,
        address: Address,
        properties: Dict[int, ExtendedProperty],
        data2: int,
        cmd2: int = 0,
        data1: int = 0x00,
    ):
        """Init the ExtendedPropertyReadManager class."""
        self._address = Address(address)
        self._write_command = ExtendedSetCommand(
            self._address, data1=data1, data2=data2, cmd2=cmd2
        )
        self._props: Dict[int, ExtendedProperty] = properties

    @property
    def is_dirty(self):
        """Return if any properties are dirty."""
        for _, prop in self._props.items():
            if prop.is_dirty:
                return True
        return False

    async def async_write(self):
        """Write the extended properties."""
        if not self.is_dirty:
            return ResponseStatus.SUCCESS

        ud_dict = {f"data{index}": _value(prop) for index, prop in self._props.items()}
        retries = RETRIES
        response = ResponseStatus.UNSENT
        while retries and response != ResponseStatus.SUCCESS:
            response = await self._write_command.async_send(**ud_dict)
            retries -= 1
            if response == ResponseStatus.SUCCESS:
                self._load_prop_values()
        return response

    def _load_prop_values(self):
        """Load the new value to the property value."""
        for _, prop in self._props.items():
            if prop.is_dirty:
                prop.set_value(prop.new_value)
