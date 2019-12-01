"""Get and Set extended properties for a device."""
from collections import namedtuple

from pyinsteon.address import Address
from pyinsteon.handlers.to_device.extended_get import ExtendedGetCommand
from pyinsteon.handlers.to_device.extended_set import ExtendedSetCommand
from pyinsteon.handlers.from_device.ext_get_response import ExtendedGetResponseHandler


PropertyInfo = namedtuple("PropertyInfo", "flag update_method group data_field bit set_cmd")


def _calc_flag_value(field):
    data = 0x00
    set_cmd = 0x00
    for bit in field:
        flag_info = field[bit]
        if flag_info.flag.new_value:
            data = data | 1 << bit
        set_cmd = flag_info.set_cmd
    return set_cmd, data


class GetSetExtendedPropertyManager():
    """Get and Set extended properties for a device."""

    def __init__(self, address: Address):
        """Init the GetSetExtendedPropertyManager class."""
        self._address = Address(address)
        self._set_command = ExtendedSetCommand(address=self._address)
        self._get_command = ExtendedGetCommand(address=self._address)
        self._get_response = ExtendedGetResponseHandler(address=self._address)
        self._get_response.subscribe(self._update_flags)
        self._groups = {}

    def subscribe(self, flag, update_method, group, data_field, bit, set_cmd):
        """Subscribe a device property to Get and Set values."""
        flag_info = PropertyInfo(flag, update_method, group, data_field, bit, set_cmd)
        flags = self._groups.get(group, {})
        field = flags.get(data_field, {})
        if bit is not None:
            field[bit] = flag_info
        else:
            field = flag_info
        flags[data_field] = field
        self._groups[group] = flags

    async def async_get(self, group=None):
        """Get the properties for a group."""
        # TODO return success or failure
        if group is None:
            for curr_group in self._groups:
                await self._get_command.async_send(group=curr_group)
        else:
            await self._get_command.async_send(group=group)

    async def async_set(self, group=None, force=False):
        """Set the properties for a group."""
        if group is None:
            for curr_group in self._groups:
                await self._set_flags_in_group(curr_group, force)
        else:
            await self._set_flags_in_group(group, force)

    async def _set_flags_in_group(self, group, force):
        for field in self._groups[group]:
            if isinstance(self._groups[group][field], PropertyInfo):
                data = self._groups[group][field].flag.new_value
                set_cmd = self._groups[group][field].set_cmd
            else:
                set_cmd, data = _calc_flag_value(self._groups[group][field])
            if set_cmd is not None:
                # TODO check for success or failure
                await self._set_command.async_send(group=group, action=set_cmd, data3=data)

    def _update_flags(self, group, data):
        """Update each flag."""
        if self._groups.get(group) is None and group == 1:
            group = 0
        if self._groups.get(group) is None:
            return
        for field in self._groups[group]:
            value = data.get('data{}'.format(field))
            if isinstance(self._groups[group][field], PropertyInfo):
                flag_info = self._groups[group][field]
                flag_info.update_method(value=value)
            else:
                for bit in self._groups[group][field]:
                    flag_info = self._groups[group][field][bit]
                    bit_value = bool(value & 1 << flag_info.bit)
                    flag_info.update_method(value=bit_value)
