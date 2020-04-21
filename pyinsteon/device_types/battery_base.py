"""Base device object."""

import asyncio
import logging
from functools import partial
from inspect import getfullargspec

from ..utils import subscribe_topic
from ..aldb.aldb_battery import ALDBBattery
from ..constants import ResponseStatus
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
        return ResponseStatus.RUN_ON_WAKE

    def close(self):
        """Close the command listener."""
        self._commands_queue.put_nowait((None, None))

    async def async_status(self, group=None):
        """Get device status."""
        args = getfullargspec(super(BatteryDeviceBase, self).async_status)
        if "group" in args[0]:
            return self._run_on_wake(
                super(BatteryDeviceBase, self).async_status, group=group
            )
        return self._run_on_wake(super(BatteryDeviceBase, self).async_status)

    async def async_read_op_flags(self):
        """Read the device operating flags."""
        return self._run_on_wake(super(BatteryDeviceBase, self).async_read_op_flags)

    async def async_write_op_flags(self):
        """Write the operating flags to the device."""
        return self._run_on_wake(super(BatteryDeviceBase, self).async_write_op_flags)

    async def async_read_ext_properties(self):
        """Get the device extended properties."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_read_ext_properties
        )

    async def async_get_engine_version(self):
        """Read the device engine version."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_get_engine_version
        )

    async def async_add_default_links(self):
        """Add default links to the device."""
        return self._run_on_wake(super(BatteryDeviceBase, self).async_add_default_links)

    async def async_read_config(self):
        """Get all configuration settings.

        This includes:
        - Operating flags
        - Extended properties
        - All-Link Database records.
        """
        return self._run_on_wake(super(BatteryDeviceBase, self).async_add_default_links)

    async def async_read_product_id(self):
        """Get the product ID."""
        return self._run_on_wake(super(BatteryDeviceBase, self).async_read_product_id)

    async def async_write_ext_properties(self):
        """Write the extended properties."""
        return self._run_on_wake(
            super(BatteryDeviceBase, self).async_write_ext_properties
        )

    async def async_keep_awake(self, awake_time=0xFF):
        """Keep the device awake to ensure commands are heard."""
        return await self._keep_awake_cmd.async_send(data3=awake_time, priority=1)

    def _device_awake(self, **kwargs):
        """Execute the commands that were requested while sleeping."""
        if self._commands_queue.empty():
            return
        if self._last_run is None or self._last_run.done():
            _LOGGER.debug("We have commands to run so let's get to it")
            self._last_run = asyncio.ensure_future(self._ensure_commands())

    async def _ensure_commands(self):
        """Ensure any commands are run."""
        keep_awake_retry = 3
        while keep_awake_retry:
            result = await self.async_keep_awake()
            _LOGGER.debug("Keep awake result: %s", str(result))
            if result == ResponseStatus.SUCCESS:
                return await self._run_commands()
            keep_awake_retry -= 1
            _LOGGER.debug("Retries: %d", keep_awake_retry)
            await asyncio.sleep(3)

    async def _run_commands(self):
        """Run the commands in queue."""
        retry_cmds = []
        while True:
            try:
                command, retries = await asyncio.wait_for(
                    self._commands_queue.get(), TIMEOUT
                )
                _LOGGER.debug("got a command to run YAY")
                _LOGGER.debug(str(command))
                if command is None:
                    return
                result = await command()
                if result != ResponseStatus.SUCCESS and retries:
                    retry_cmds.append((command, retries - 1))
            except asyncio.TimeoutError:
                break

        for cmd, retries in retry_cmds:
            self._run_on_wake(cmd, retries)
