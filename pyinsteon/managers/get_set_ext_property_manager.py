"""Get and Set extended properties for a device."""
import asyncio
from collections import namedtuple
import logging
from typing import Dict, Union

from ..address import Address
from ..config.extended_property import ExtendedProperty
from ..constants import PropertyType, ResponseStatus
from ..handlers.from_device.ext_get_response import ExtendedGetResponseHandler
from ..handlers.to_device.extended_get import ExtendedGetCommand
from ..handlers.to_device.extended_set import ExtendedSetCommand
from ..subscriber_base import SubscriberBase
from ..topics import EXTENDED_PROPERTIES_CHANGED
from ..utils import multiple_status

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 2
RETRIES = 20

PropertyInfo = namedtuple(
    "PropertyInfo", "name group data_field bit set_cmd update_field"
)


class GetSetExtendedPropertyManager(SubscriberBase):
    """Get and Set extended properties for a device."""

    def __init__(self, address: Address):
        """Init the GetSetExtendedPropertyManager class."""
        self._address = Address(address)
        super().__init__(f"{self._address.id}.{EXTENDED_PROPERTIES_CHANGED}")

        self._properties: Dict[str, ExtendedProperty] = {}
        self._get_command = ExtendedGetCommand(address=self._address)
        self._get_response = ExtendedGetResponseHandler(address=self._address)
        self._get_response.subscribe(self._handle_get_response)
        self._prop_groups: Dict[int, PropertyInfo | Dict[int, PropertyInfo]] = {}
        self._flags: Dict[str, PropertyInfo] = {}
        self._response_queue = asyncio.Queue()
        self._get_cmd_lock = asyncio.Lock()

    @property
    def flag_info(self):
        """Return the flag information."""
        return self._flags

    def create(
        self,
        name,
        group,
        data_field,
        bit,
        set_cmd,
        is_revsersed=False,
        prop_type=PropertyType.STANDARD,
        update_field=3,
    ):
        """Subscribe a device property to Get and Set values.

        data is stored in self._prop_groups[group][data_field]<[bit]>
        """
        value_type = bool if bit is not None else int
        flag_info = PropertyInfo(name, group, data_field, bit, set_cmd, update_field)
        flags = self._prop_groups.get(group, {})
        if bit is not None:
            field = flags.get(data_field, {})
            field[bit] = flag_info
        else:
            field = flag_info
        flags[data_field] = field
        self._prop_groups[group] = flags
        self._flags[name] = flag_info
        read_only = set_cmd is None
        self._properties[name] = ExtendedProperty(
            self._address, name, value_type, is_revsersed, read_only, prop_type
        )
        return self._properties[name]

    async def async_read(self, group=None):
        """Get the properties for a group."""
        if self._get_cmd_lock.locked():
            self._get_cmd_lock.release()

        while not self._response_queue.empty():
            self._response_queue.get_nowait()

        async with self._get_cmd_lock:
            if group is None:
                results = []
                for curr_group in self._prop_groups:
                    result = await self._async_read(group=curr_group)
                    results.append(result)
                    await asyncio.sleep(2)
                return multiple_status(*results)
            result = await self._async_read(group=group)
        self._call_subscribers()
        return result

    async def async_write(self):
        """Set the properties for a group."""
        results = []
        for name, prop in self._properties.items():
            if prop.is_dirty:
                set_cmd = self._flags[name].set_cmd
                if set_cmd is not None:
                    result = await self._write_flag(set_cmd)
                    results.append(result)
        self._call_subscribers()
        return multiple_status(*results)

    async def _async_read(self, group):
        retry = 0
        result = ResponseStatus.UNSENT
        while retry < RETRIES and result != ResponseStatus.SUCCESS:
            await self._get_command.async_send(group=group)
            result = await self._wait_for_get()
            retry += 1
        return result

    async def _wait_for_get(self):
        """Wait for the get response message."""
        try:
            return await asyncio.wait_for(self._response_queue.get(), TIMEOUT)
        except asyncio.TimeoutError:
            return ResponseStatus.FAILURE

    async def _write_flag(self, set_cmd):
        """Write a flag to a device."""
        if set_cmd is None:
            return ResponseStatus.SUCCESS
        cmd = ExtendedSetCommand(self._address, data1=0, data2=set_cmd)
        data_fields, prop_info_list = self._get_data_fields(set_cmd)
        result = await cmd.async_send(**data_fields)
        if result == ResponseStatus.SUCCESS:
            self._update_set_fields(prop_info_list)
        return result

    def _get_data_fields(
        self, set_cmd
    ) -> Union[Dict[str, int], Dict[str, PropertyInfo]]:
        """Get all data elements for the same set command."""
        prop_info_list: Dict[str, PropertyInfo] = {}
        for name, flag_info in self._flags.items():
            if flag_info.set_cmd == set_cmd and name not in prop_info_list:
                prop_info_list[name] = flag_info
        data_fields: Dict[str, int] = {}
        # group_bits = []
        for name, prop_info in prop_info_list.items():
            if prop_info.bit is None:
                prop = self._properties[name]
                group = prop_info.group
                value = prop.new_value if prop.is_dirty else prop.value
            else:
                field = prop_info.data_field
                value = self._calc_flag_value(self._prop_groups[group][field])

            data_fields[f"data{prop_info.update_field}"] = value
        return data_fields, prop_info_list

    def _handle_get_response(self, group, data):
        """Handle the response from a get command."""
        if not self._get_cmd_lock.locked():
            return
        if self._prop_groups.get(group) is None and group == 1:
            group = 0
        if self._prop_groups.get(group) is None:
            return
        for field in self._prop_groups[group]:
            value = data.get(f"data{field}")
            self._update_one_field(group=group, field=field, value=value)
        self._response_queue.put_nowait(ResponseStatus.SUCCESS)

    def _update_set_fields(self, prop_info_list: Dict[str, PropertyInfo]):
        """Update all the fields in a successful set command."""
        for name, _ in prop_info_list.items():
            prop = self._properties[name]
            if prop.is_dirty:
                prop.set_value(prop.new_value)

    def _update_one_field(self, group, field, value):
        """Update one field including bit based fields."""
        if isinstance(self._prop_groups[group][field], PropertyInfo):
            flag_info = self._prop_groups[group][field]
            flag = self._properties[flag_info.name]
            flag.set_value(value=value)
        else:
            for bit in self._prop_groups[group][field]:
                flag_info = self._prop_groups[group][field][bit]
                bit_value = bool(value & 1 << flag_info.bit)
                flag = self._properties[flag_info.name]
                flag.set_value(value=bit_value)
        self._response_queue.put_nowait(ResponseStatus.SUCCESS)

    def _calc_flag_value(self, field):
        data = 0x00
        for bit in field:
            flag_info = field[bit]
            flag = self._properties[flag_info.name]
            set_value = not flag.new_value if flag.is_reversed else flag.new_value
            if set_value:
                data = data | 1 << bit
        return data
