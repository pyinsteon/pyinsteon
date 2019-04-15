"""Insteon Modem Base Class."""
from abc import ABCMeta
import asyncio
from . import Device
from ..aldb import ModemALDB


class ModemBase(Device, metaclass=ABCMeta):
    """Base class for insteon Modems (PLM and Hub)."""

    __meta__ = ABCMeta

    def __init__(self, protocol, transport, workdir='', address='000000',
                 cat=0x03, subcat=0x00, firmware=0x00,
                 description='', model=''):
        """Init the Modem class."""
        super().__init__(address, cat, subcat, firmware, description, model)
        self._aldb = ModemALDB(self._address)
        self._subscribe_topics()
        self._protocol = protocol
        self._transport = transport

    @property
    def connected(self) -> bool:
        """Return true if the transport is connected."""
        return self._protocol.connected

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

    def _subscribe_topics(self):
        """Subscribe to modem specific topics."""
    #     pub.subscribe(self.connect, "connection.lost")

    def _register_states(self):
        """No states to register for modems."""

    def _register_default_links(self):
        """No default links for modems."""

    def _register_handlers(self):
        """Register command handlers for modems."""
