"""Insteon Modem Base Class."""
import asyncio
from abc import ABCMeta
from asyncio import Transport

from ..config import (
    AUTO_LED,
    DEADMAN,
    DISABLE_AUTO_LINKING,
    MONITOR_MODE,
    get_usable_value,
)
from ..config.modem_config import ModemConfiguration
from ..constants import ResponseStatus
from ..handlers.all_link_cleanup_failure_report import AllLinkCleanupFailureReport
from ..handlers.all_link_cleanup_status_report import AllLinkCleanupStatusReport
from ..handlers.get_im_configuration import GetImConfigurationHandler
from ..handlers.set_im_configuration import SetImConfigurationHandler
from ..protocol.protocol import Protocol
from ..utils import multiple_status
from .device_base import Device
from .device_commands import GET_IM_CONFIG_COMMAND, SET_IM_CONFIG_COMMAND


class ModemBase(Device, metaclass=ABCMeta):
    """Base class for insteon Modems (PLM and Hub)."""

    __meta__ = ABCMeta

    def __init__(
        self,
        address="000000",
        cat=0x03,
        subcat=0x00,
        firmware=0x00,
        description="",
        model="",
    ):
        """Init the Modem class."""
        super().__init__(address, cat, subcat, firmware, description, model)
        self._aldb = None
        self._subscribe_topics()
        self._protocol = None
        self._transport = None
        self._io_manager = None

    @property
    def connected(self) -> bool:
        """Return true if the transport is connected."""
        if not self._protocol:
            return False
        return self._protocol.connected

    @property
    def protocol(self):
        """Return the protocol."""
        return self._protocol

    @property
    def disable_auto_linking(self):
        """Return the Disable Auto Linking flag value."""
        return self._config[DISABLE_AUTO_LINKING].value

    @property
    def monitor_mode(self):
        """Return the Monitor Mode flag value."""
        return self._config[MONITOR_MODE].value

    @property
    def auto_led(self):
        """Return the Auto LED flag value."""
        return self._config[AUTO_LED].value

    @property
    def deadman(self):
        """Return the Deadman flag value."""
        return self._config[DEADMAN].value

    @protocol.setter
    def protocol(self, value):
        """Set the protocol."""
        if isinstance(value, Protocol):
            self._protocol = value

    @property
    def transport(self):
        """Return the transport."""
        return self._transport

    @transport.setter
    def transport(self, value):
        """Set the transport."""
        if isinstance(value, Transport):
            self._transport = value

    def close(self):
        """Close the connection to the transport."""
        asyncio.ensure_future(self.async_close())

    async def async_close(self):
        """Close the connection to the transport ascynronously."""
        if self._protocol:
            self._protocol.close()
            wait_time = 0.0001
            while self.connected:
                await asyncio.sleep(wait_time)
                wait_time = min(300, 1.5 * wait_time)

    async def async_get_configuration(self):
        """Get the modem flags."""
        return await self._handlers[GET_IM_CONFIG_COMMAND].async_send()

    async def async_set_configuration(
        self,
        disable_auto_linking: bool = None,
        monitor_mode: bool = None,
        auto_led: bool = None,
        deadman: bool = None,
    ):
        """Set the modem flags."""
        self._config[DISABLE_AUTO_LINKING].new_value = disable_auto_linking
        self._config[MONITOR_MODE].new_value = monitor_mode
        self._config[AUTO_LED].new_value = auto_led
        self._config[DEADMAN].new_value = deadman

        disable_auto_linking = get_usable_value(self._config[DISABLE_AUTO_LINKING])
        monitor_mode = get_usable_value(self._config[MONITOR_MODE])
        auto_led = get_usable_value(self._config[AUTO_LED])
        deadman = get_usable_value(self._config[DEADMAN])

        return await self._handlers[SET_IM_CONFIG_COMMAND].async_send(
            disable_auto_linking=disable_auto_linking,
            monitor_mode=monitor_mode,
            auto_led=auto_led,
            deadman=deadman,
        )

    async def async_read_config(self, read_aldb: bool = True):
        """Read the modem configuration."""
        result_config = await self.async_get_configuration()
        if read_aldb:
            result_aldb = await self.aldb.async_load()
        else:
            result_aldb = ResponseStatus.SUCCESS
        return multiple_status(result_config, result_aldb)

    async def async_write_config(self):
        """Write the configuration changes to the modem."""
        if (
            self._config[DISABLE_AUTO_LINKING].is_dirty
            or self._config[MONITOR_MODE].is_dirty
            or self._config[AUTO_LED].is_dirty
            or self._config[DEADMAN].is_dirty
        ):
            disable_auto_linking = get_usable_value(self._config[DISABLE_AUTO_LINKING])
            monitor_mode = get_usable_value(self._config[MONITOR_MODE])
            auto_led = get_usable_value(self._config[AUTO_LED])
            deadman = get_usable_value(self._config[DEADMAN])

            return await self._handlers[SET_IM_CONFIG_COMMAND].async_send(
                disable_auto_linking=disable_auto_linking,
                monitor_mode=monitor_mode,
                auto_led=auto_led,
                deadman=deadman,
            )
        return ResponseStatus.SUCCESS

    async def async_get_operating_flags(self, group=None):
        """Read the device operating flags."""
        return await self.async_get_configuration()

    async def async_set_operating_flags(self, group=None, force=False):
        """Write the operating flags to the device."""
        return await self.async_set_configuration(
            self._config[DISABLE_AUTO_LINKING].new_value,
            self._config[MONITOR_MODE].new_value,
            self._config[AUTO_LED].new_value,
            self._config[DEADMAN].new_value,
        )

    async def async_get_extended_properties(self, group=None):
        """Get the device extended properties."""

    def _subscribe_topics(self):
        """Subscribe to modem specific topics."""

    def _update_flags(
        self,
        disable_auto_linking: bool,
        monitor_mode: bool,
        auto_led: bool,
        deadman: bool,
    ):
        self._config[DISABLE_AUTO_LINKING].load(disable_auto_linking)
        self._config[MONITOR_MODE].load(monitor_mode)
        self._config[AUTO_LED].load(auto_led)
        self._config[DEADMAN].load(deadman)

    def _register_groups(self):
        """No groups to register for modems."""

    def _register_default_links(self):
        """No default links for modems."""

    def _register_handlers_and_managers(self):
        """Register command handlers for modems."""
        super()._register_handlers_and_managers()
        self._handlers["cleanup_status_report"] = AllLinkCleanupStatusReport()
        self._handlers["cleanup_failure_report"] = AllLinkCleanupFailureReport()
        self._handlers[GET_IM_CONFIG_COMMAND] = GetImConfigurationHandler()
        self._handlers[GET_IM_CONFIG_COMMAND].subscribe(self._update_flags)

        self._handlers[SET_IM_CONFIG_COMMAND] = SetImConfigurationHandler()
        self._handlers[SET_IM_CONFIG_COMMAND].subscribe(self._update_flags)

    def _register_events(self):
        """Register events for modems."""

    def _register_op_flags_and_props(self):
        """Register operating flags for modem."""

    def _register_config(self):
        """Register the configuration items of a modem."""
        super()._register_config()
        self._config[DISABLE_AUTO_LINKING] = ModemConfiguration(
            self._address, DISABLE_AUTO_LINKING
        )
        self._config[MONITOR_MODE] = ModemConfiguration(self._address, MONITOR_MODE)
        self._config[AUTO_LED] = ModemConfiguration(self._address, AUTO_LED)
        self._config[DEADMAN] = ModemConfiguration(self._address, DEADMAN)
