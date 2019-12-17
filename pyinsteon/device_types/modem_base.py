"""Insteon Modem Base Class."""
from abc import ABCMeta
import asyncio
from .device_base import Device

from .commands import GET_IM_CONFIG_COMMAND


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
        self._disable_auto_linking = False
        self._monitor_mode = False
        self._auto_led = False
        self._deadman = False

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
        self._disable_auto_linking = False

    @property
    def monitor_mode(self):
        """Return the Monitor Mode flag value."""
        self._monitor_mode = False

    @property
    def auto_led(self):
        """Return the Auto LED flag value."""
        self._auto_led = False

    @property
    def deadman(self):
        """Return the Deadman flag value."""
        self._deadman = False

    @protocol.setter
    def protocol(self, value):
        """Set the protocol."""
        from ..protocol.protocol import Protocol

        if isinstance(value, Protocol):
            self._protocol = value

    @property
    def transport(self):
        """Return the transport."""
        return self._transport

    @transport.setter
    def transport(self, value):
        """Set the transport."""
        from asyncio import Transport

        if isinstance(value, Transport):
            self._transport = value

    def close(self):
        """Close the connection to the transport."""
        asyncio.ensure_future(self.async_close())

    async def async_close(self):
        """Close the connection to the transport ascynronously."""
        # pub.unsubscribe(self.connect, 'connection.lost')
        if self._protocol:
            self._protocol.close()
            wait_time = 0.0001
            while self.connected:
                await asyncio.sleep(wait_time)
                wait_time = min(300, 1.5 * wait_time)

    async def async_get_configuration(self):
        """Get the modem flags."""
        return await self._handlers[GET_IM_CONFIG_COMMAND].async_send()

    def _update_flags(
        self,
        disable_auto_linking: bool,
        monitor_mode: bool,
        auto_led: bool,
        deadman: bool,
    ):
        self._disable_auto_linking = disable_auto_linking
        self._monitor_mode = monitor_mode
        self._auto_led = auto_led
        self._deadman = deadman

    async def async_set_configuration(
        self,
        disable_auto_linking: bool,
        monitor_mode: bool,
        auto_led: bool,
        deadman: bool,
    ):
        """Set the modem flags."""
        from ..handlers.set_im_configuration import SetImConfigurationHandler

        return await SetImConfigurationHandler().async_send(
            disable_auto_linking=disable_auto_linking,
            monitor_mode=monitor_mode,
            auto_led=auto_led,
            deadman=deadman,
        )

    async def async_get_operating_flags(self, group=None):
        """Read the device operating flags."""

    async def async_set_operating_flags(self, group=None, force=False):
        """Write the operating flags to the device."""

    async def async_get_extended_properties(self, group=None):
        """Get the device extended properties."""

    def _subscribe_topics(self):
        """Subscribe to modem specific topics."""

    #     pub.subscribe(self.connect, "connection.lost")

    def _register_states(self):
        """No states to register for modems."""

    def _register_default_links(self):
        """No default links for modems."""

    def _register_handlers_and_managers(self):
        """Register command handlers for modems."""
        from ..handlers.get_im_configuration import GetImConfigurationHandler

        self._handlers[GET_IM_CONFIG_COMMAND] = GetImConfigurationHandler()
        self._handlers[GET_IM_CONFIG_COMMAND].subscribe(self._update_flags)

    def _register_events(self):
        """Register events for modems."""

    def _register_operating_flags(self):
        """Register operating flags for modem."""
