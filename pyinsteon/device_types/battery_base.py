"""Base device object."""

import asyncio
from functools import partial
import logging

from .. import pub
from ..handlers.to_device.extended_set import ExtendedSetCommand


_LOGGER = logging.getLogger(__name__)
TIMEOUT = 2


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
            **kwargs,
        )
        self._is_battery = True
        self._commands_queue = asyncio.Queue()
        self._aldb = ALDBBattery(address=address, run_command=self._run_on_wake)
        self._last_run = None
        pub.subscribe(self._device_awake, self._address.id)
        asyncio.ensure_future(self.async_keep_awake())

    def _run_on_wake(self, command, retries=3, **kwargs):
        cmd = partial(command, **kwargs)
        self._commands_queue.put_nowait((cmd, retries))

    async def async_read_op_flags(self):
        """Read the device operating flags."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_read_op_flags)

    async def async_write_op_flags(self):
        """Write the operating flags to the device."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_write_op_flags)

    async def async_read_ext_properties(self):
        """Get the device extended properties."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_read_ext_properties)

    async def async_keep_awake(self, awake_time=0xFF):
        """Keep the device awake to ensure commands are heard."""
        cmd = ExtendedSetCommand(self._address, data1=0, data2=0x04)
        return await cmd.async_send(data3=awake_time)

    def _device_awake(self, topic=pub.AUTO_TOPIC, **kwargs):
        """Execute the commands that were requested while sleeping."""
        if self._last_run is None or self._last_run.done():
            self._last_run = asyncio.ensure_future(self._run_commands())

    async def _run_commands(self):
        from inspect import iscoroutinefunction, iscoroutine

        await asyncio.sleep(1)
        retry_cmds = []
        try:
            while True:
                command, retries = await asyncio.wait_for(
                    self._commands_queue.get(), TIMEOUT
                )
                await self.async_keep_awake()
                if isinstance(command, partial):
                    if iscoroutine(command.func) or iscoroutinefunction(command.func):
                        result = await command()
                    else:
                        result = command()
                elif iscoroutine(command) or iscoroutinefunction(command):
                    result = await command()
                else:
                    result = command()
                if int(result) != 1 and retries:
                    retry_cmds.append((command, retries - 1))
        except asyncio.TimeoutError:
            pass
        for cmd, retries in retry_cmds:
            self._run_on_wake(cmd, retries)
