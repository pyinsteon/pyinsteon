"""Base device object."""

import asyncio
import logging
from functools import partial
from inspect import iscoroutine, iscoroutinefunction

from ..utils import subscribe_topic
from ..aldb.aldb_battery import ALDBBattery
from ..constants import ResponseStatus
from ..handlers.to_device.extended_set import ExtendedSetCommand

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 2


async def _run_command(command):
    """Run an individual command."""
    if isinstance(command, partial):
        _LOGGER.error("Command is a partial")
        if iscoroutine(command.func) or iscoroutinefunction(command.func):
            _LOGGER.error("Command is a coroutine (partial)")
            return await command()
    if iscoroutine(command) or iscoroutinefunction(command):
        _LOGGER.error("Command is a coroutine (not partial)")
        return await command()
    _LOGGER.error("Command is just a command")
    return command()


# pylint: disable=no-member
class BatteryDeviceBase:
    """Base class for battery operated devices."""

    def __init__(
        self, address, cat, subcat, firmware=0x00, description="", model="", **kwargs
    ):
        """Init the DeviceBattery class."""

        # The super class is the non-battery base class such as OnOffControllerBase
        super(BatteryDeviceBase, self).__init__(
            address=address,
            cat=cat,
            subcat=subcat,
            firmware=0x00,
            description=description,
            model=model,
            **kwargs,
        )
        self._is_battery = True
        self._commands_queue = asyncio.Queue()
        self._aldb = ALDBBattery(address=address, run_command=self._run_on_wake)
        self._last_run = None
        self._keep_awake_cmd = ExtendedSetCommand(self._address, data1=0, data2=0x04)
        subscribe_topic(self._device_awake, self._address.id)
        # This may or may not make sense.
        # It it helps to set default links when the device first connect,
        # then this probably makes sense.
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

    async def async_add_default_links(self):
        """Add default links to the device."""
        self._run_on_wake(super(BatteryDeviceBase, self).async_add_default_links)

    async def async_keep_awake(self, awake_time=0xFF):
        """Keep the device awake to ensure commands are heard."""
        return await self._keep_awake_cmd.async_send(data3=awake_time, priority=1)

    def _device_awake(self, **kwargs):
        """Execute the commands that were requested while sleeping."""
        if self._commands_queue.empty():
            return
        if self._last_run is None or self._last_run.done():
            _LOGGER.error("We have commands to run so let's get to it")
            self._last_run = asyncio.ensure_future(self._ensure_commands())

    async def _ensure_commands(self):
        """Ensure any commands are run."""
        keep_awake_retry = 3
        while keep_awake_retry:
            result = await self.async_keep_awake()
            _LOGGER.error("Keep awake result: %s", str(result))
            if result == ResponseStatus.SUCCESS:
                return await self._run_commands()
            keep_awake_retry -= 1
            _LOGGER.error("Retries: %d", keep_awake_retry)
            await asyncio.sleep(3)

    async def _run_commands(self):
        """Run the commands in queue."""
        retry_cmds = []
        while True:
            try:
                command, retries = await asyncio.wait_for(
                    self._commands_queue.get(), TIMEOUT
                )
                _LOGGER.error("got a command to run YAY")
                _LOGGER.error(str(command))
                result = await _run_command(command)
                if result != ResponseStatus.SUCCESS and retries:
                    retry_cmds.append((command, retries - 1))
            except asyncio.TimeoutError:
                break

        for cmd, retries in retry_cmds:
            self._run_on_wake(cmd, retries)
