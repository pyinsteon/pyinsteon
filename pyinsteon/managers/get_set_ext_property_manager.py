"""Get and Set extended properties for a device."""
import asyncio
from collections import namedtuple
import logging

from ..extended_property import ExtendedProperty
from ..address import Address
from ..handlers.to_device.extended_get import ExtendedGetCommand
from ..handlers.to_device.extended_set import ExtendedSetCommand
from ..handlers.from_device.ext_get_response import ExtendedGetResponseHandler
from ..constants import ResponseStatus
from ..utils import multiple_status


_LOGGER = logging.getLogger(__name__)
TIMEOUT = 2
RETRIES = 20

PropertyInfo = namedtuple("PropertyInfo", "name group data_field bit set_cmd")


def _calc_flag_value(field):
    data = 0x00
    set_cmd = None
    for bit in field:
        flag_info = field[bit]
        if flag_info.flag.new_value:
            data = data | 1 << bit
        set_cmd = flag_info.set_cmd
    return set_cmd, data


class GetSetExtendedPropertyManager:
    """Get and Set extended properties for a device."""

    def __init__(self, address: Address):
        """Init the GetSetExtendedPropertyManager class."""
        self._address = Address(address)
        self._properties = {}
        self._get_command = ExtendedGetCommand(address=self._address)
        self._get_response = ExtendedGetResponseHandler(address=self._address)
        self._get_response.subscribe(self._update_all_fields)
        self._groups = {}
        self._flags = {}
        self._response_queue = asyncio.Queue()

    def create(self, name, group, data_field, bit, set_cmd):
        """Subscribe a device property to Get and Set values.

        data is stored in self._groups[group][data_field]<[bit]>
        """
        prop_type = bool if bit is not None else int
        flag_info = PropertyInfo(name, group, data_field, bit, set_cmd)
        flags = self._groups.get(group, {})
        field = flags.get(data_field, {})
        if bit is not None:
            field[bit] = flag_info
        else:
            field = flag_info
        flags[data_field] = field
        self._groups[group] = flags
        self._flags[name] = flag_info
        self._properties[name] = ExtendedProperty(self._address, name, prop_type)
        return self._properties[name]

    async def async_read(self, group=None):
        """Get the properties for a group."""
        while not self._response_queue.empty():
            self._response_queue.get_nowait()
        if group is None:
            results = []
            for curr_group in self._groups:
                result = await self._async_read(group=curr_group)
                results.append(result)
            return multiple_status(*results)
        return await self._async_read(group=group)

    async def _async_read(self, group):
        retry = 0
        result = ResponseStatus.UNSENT
        while retry < RETRIES and result != ResponseStatus.SUCCESS:
            await self._get_command.async_send(group=group)
            result = await self._wait_for_get()
            retry += 1
        return result

    async def async_write(self):
        """Set the properties for a group."""
        results = []
        for name in self._properties:
            if self._properties[name].is_dirty:
                group = self._flags[name].group
                data_field = self._flags[name].data_field
                result = await self._write_flag(name, group, data_field)
                results.append(result)
        return multiple_status(*results)

    async def _wait_for_get(self):
        """Wait for the get response message."""
        try:
            return await asyncio.wait_for(self._response_queue.get(), TIMEOUT)
        except asyncio.TimeoutError:
            return ResponseStatus.FAILURE

    async def _write_flag(self, name, group, field):
        """Write a flag to a device."""
        flag = self._properties[name]
        if isinstance(self._groups[group][field], PropertyInfo):
            data = flag.new_value
            set_cmd = self._groups[group][field].set_cmd
        else:
            set_cmd, data = _calc_flag_value(self._groups[group][field])
        if set_cmd is not None:
            cmd = ExtendedSetCommand(self._address, data1=group, data2=set_cmd)
            result = await cmd.async_send(data3=data)
            if result == ResponseStatus.SUCCESS:
                self._update_one_field(group, field, data)
            return result

    def _update_all_fields(self, group, data):
        """Update each flag."""
        _LOGGER.error("Found a new extended flag set")
        if self._groups.get(group) is None and group == 1:
            group = 0
        if self._groups.get(group) is None:
            return
        for field in self._groups[group]:
            value = data.get("data{}".format(field))
            self._update_one_field(group=group, field=field, value=value)
        self._response_queue.put_nowait(ResponseStatus.SUCCESS)

    def _update_one_field(self, group, field, value):
        """Update one field including bit based fields."""
        if isinstance(self._groups[group][field], PropertyInfo):
            flag_info = self._groups[group][field]
            flag = self._properties[flag_info.name]
            flag.load(value=value)
        else:
            for bit in self._groups[group][field]:
                flag_info = self._groups[group][field][bit]
                bit_value = bool(value & 1 << flag_info.bit)
                flag = self._properties[flag_info.name]
                flag.load(value=bit_value)
        self._response_queue.put_nowait(ResponseStatus.SUCCESS)
