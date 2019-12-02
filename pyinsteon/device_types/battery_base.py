"""Base device object."""

from abc import ABC
import asyncio
from datetime import datetime
from functools import partial
import logging

from .. import pub
from ..address import Address
from ..aldb import ALDB
from ..managers.get_set_op_flag_manager import GetSetOperatingFlagsManager
from ..managers.get_set_ext_property_manager import GetSetExtendedPropertyManager
from ..handlers.to_device.extended_set import ExtendedSetCommand
from ..operating_flag import OperatingFlag
from ..extended_property import ExtendedProperty
from .commands import (
    EXTENDED_GET_COMMAND,
    EXTENDED_SET_COMMAND,
    GET_OPERATING_FLAGS_COMMAND,
    SET_OPERATING_FLAGS_COMMAND,
    EXTENDED_GET_RESPONSE,
    ON_ALL_LINK_CLEANUP,
    OFF_ALL_LINK_CLEANUP,
)

_LOGGER = logging.getLogger(__name__)


# pylint: disable=no-member
class BatteryDeviceBase:
    """Base class for battery operated devices."""

    def __init__(
        self, address, cat, subcat, firmware=0x00, description="", model="", **kwargs
    ):
        """Init the DeviceBattery class."""
        from ..aldb.aldb_battery import ALDBBattery

        # The super class is the non-battery base class such as OnOffControllerBase
        super(BatteryDeviceBase, self).__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=0x00,
            description="",
            model="",
            **kwargs
        )
        self._aldb = ALDBBattery(address=address)
        self._commands_queue = asyncio.Queue()
        pub.subscribe(self._device_awake, self._address.id)
        pub.subscribe(self._load_aldb, "{}.aldb.load".format(self._address.id))
        pub.subscribe(self._write_aldb, "{}.aldb.write".format(self._address.id))

    def _run_on_wake(self, command, **kwargs):
        cmd = partial(command, **kwargs)
        self._commands_queue.put_nowait(cmd)

    async def async_get_operating_flags(self):
        """Read the device operating flags."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_get_operating_flags)

    async def async_set_operating_flags(self):
        """Write the operating flags to the device."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_set_operating_flags)

    async def async_get_extended_properties(self):
        """Get the device extended properties."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_get_extended_properties)

    async def async_keep_awake(self, awake_time=0xFF):
        """Keep the device awake to ensure commands are heard."""
        cmd = ExtendedSetCommand(self._address)
        return await cmd.async_send(group=0, action=0x04, data3=awake_time)

    def _device_awake(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Execute the commands that were requested while sleeping."""
        asyncio.ensure_future(self._run_commands())

    async def _run_commands(self):
        from inspect import iscoroutinefunction, iscoroutine

        if not self._commands_queue.empty():
            _LOGGER.debug(
                "Sending commands to battery operated device %s", self._address
            )
            await self.async_keep_awake()
        while not self._commands_queue.empty():
            command = await self._commands_queue.get()
            if isinstance(command, partial):
                if iscoroutine(command.func) or iscoroutinefunction(command.func):
                    await command()
                else:
                    command()
            elif iscoroutine(command) or iscoroutinefunction(command):
                await command()
            else:
                command()

    def _load_aldb(self, mem_addr, num_recs, refresh, callback):
        cmd = partial(
            self._aldb.async_load,
            mem_addr=mem_addr,
            num_recs=num_recs,
            refresh=refresh,
            callback=callback,
        )
        self._commands_queue.put_nowait(cmd)

    def _write_aldb(self):
        cmd = partial(self._aldb.async_write_records)
        self._commands_queue.put_nowait(cmd)
