"""Insteon Modem Base Class."""
from abc import ABCMeta
import asyncio
from . import Device
from ..aldb.modem_aldb import ModemALDB


class ModemBase(Device, metaclass=ABCMeta):
    """Base class for insteon Modems (PLM and Hub)."""

    __meta__ = ABCMeta

    def __init__(self, address='000000', cat=0x03, subcat=0x00, firmware=0x00,
                 description='', model=''):
        """Init the Modem class."""
        super().__init__(address, cat, subcat, firmware, description, model)
        self._aldb = ModemALDB(self._address)
        self._subscribe_topics()
        self._protocol = None
        self._transport = None

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
            WAIT_TIME = .0001
            while self.connected:
                await asyncio.sleep(WAIT_TIME)
                WAIT_TIME = min(300, 1.5 * WAIT_TIME)

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

    def _register_handlers(self):
        """Register command handlers for modems."""

    def _register_events(self):
        """Register events for modems."""

    def _register_operating_flags(self):
        """Register operating flags for modem."""
