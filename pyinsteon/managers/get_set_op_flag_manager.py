"""Manage getting an operating flag."""
import asyncio
from collections import namedtuple
import logging

from pyinsteon.address import Address
from pyinsteon.handlers.to_device.get_operating_flags import GetOperatingFlagsCommand
from pyinsteon.handlers.to_device.set_operating_flags import SetOperatingFlagsCommand

OperatingFlagInfo = namedtuple("FlagInfo", "flag update_method group bit set_cmd unset_cmd")
_LOGGER = logging.getLogger(__name__)

class GetSetOperatingFlagsManager():
    """Manager to get operating flags."""

    def __init__(self, address: Address):
        """Init the GetOperatingFlagsManager class."""
        self._address = Address(address)
        self._groups = {}
        self._get_command = GetOperatingFlagsCommand(self._address)
        self._set_command = SetOperatingFlagsCommand(self._address)
        self._send_lock = asyncio.Lock()

    def subscribe(self, flag, update_method, group, bit, set_cmd, unset_cmd):
        """Subscribe to updates."""
        flag_info = OperatingFlagInfo(flag, update_method, group, bit, set_cmd, unset_cmd)
        if group not in self._groups.keys():
            self._groups[group] = {}
        key = bit if bit is not None else 0
        self._groups[group][key] = flag_info

    def unsubscribe(self, name, group):
        """Remove a flag from updates."""
        if self._groups.get(group) is None:
            return
        flag_key = None
        for key in self._groups.get(group):
            flag_info = self._groups[group][key]
            if flag_info.flag.name == name:
                flag_key = key
                break
        if flag_key is not None:
            self._groups[group].pop(flag_key)
            if not self._groups[group]:
                self._groups.pop(group)

    async def async_get(self, group=None):
        """Get the operating flags."""
        if group is None:
            for curr_group in self._groups:
                await self._fetch_flags_in_group(curr_group)
        else:
            await self._fetch_flags_in_group(group)

    async def async_set(self, group=None, force=False):
        """Set the operating flags."""
        if group is None:
            for curr_group in self._groups:
                self._set_flags_in_group(curr_group, force)
        else:
            self._set_flags_in_group(curr_group, force)

    async def _set_flags_in_group(self, group, force):
        flags = self._groups[group]
        for key in flags:
            flag_info = flags[key]
            flag = flag_info.flag
            if flag.is_dirty or force:
                cmd = flag.set_cmd if flag.new_value else flag.unset_cmd
                if cmd is not None:  # The operating flag is read only
                    # TODO  check for success or failure
                    result = await self._set_command.async_send(cmd=cmd)
                    if int(result) == 1:
                        flag.update_method(flag.new_value)

    def _calc_flag_value(self, group):
        flags = 0x00
        for flag in self._groups[group]:
            bit = flag.bit
            value = 1 if bool(flag.flag) else 0
            flags = flags | value << bit
        return flags

    async def _fetch_flags_in_group(self, group):
        def _update_flags(flags):
            """Update each flag."""
            for key in self._groups[group]:
                flag_info = self._groups[group][key]
                if flag_info.bit is not None:
                    value = bool(flags & 1 << flag_info.bit)
                else:
                    value = flags  # the flag is the full byte
                flag_info.update_method(value=value)
        self._get_command.subscribe(_update_flags)
        # TODO check for success or failure
        await self._get_command.async_send(flags_requested=group)
        self._get_command.unsubscribe(_update_flags)

    def is_dirty(self, group=None):
        """Return if the underlying flags need to be updated on the device."""
        from functools import reduce
        if group is None:
            test = [False]
            test.extend([k for k in self._groups])
            return reduce((lambda x, y: x or self._is_group_dirty(y)), test)
        return self._is_group_dirty(group)

    def _is_group_dirty(self, group):
        """Return if the flags in a group need to be updated on the device."""
        from functools import reduce
        flags = self._groups.get(group)
        if not flags:
            return False
        test = [False]
        test.extend([f.flag for f in flags])
        return reduce((lambda x, y: x or y.is_dirty), test)
