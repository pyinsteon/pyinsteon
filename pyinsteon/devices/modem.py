"""Insteon Modem Base Class."""
from abc import ABCMeta, abstractmethod
import asyncio
from . import Device
from .. import pub
from ..aldb import ModemALDB


class Modem(Device, metaclass=ABCMeta):
    """Base class for insteon Modems (PLM and Hub)."""

    def __init__(self, workdir=''):
        """Init the Modem class."""
        super().__init__('000000', 0x03, 0x00, 0x00)
        self._aldb = ModemALDB(self._address)
        self._subscribe_topics()
        self._protocol = None
        self._transport = None

    @property
    def connected(self) -> bool:
        """Return true if the transport is connected."""
        return self._protocol.connected

    def connect(self):
        """Connect to the transport."""
        asyncio.ensure_future(self.async_connect())

    @abstractmethod
    async def async_connect(self):
        """Connect to the transport ascynronously."""

    def close(self):
        """Close the connection to the transport."""
        asyncio.ensure_future(self.async_close())

    async def async_close(self):
        """Close the connection to the transport ascynronously."""
        pub.unsubscribe(self.connect, 'connection.lost')
        if self._protocol:
            self._protocol.close()
            WAIT_TIME = .0001
            while self.connected:
                await asyncio.sleep(WAIT_TIME)
                WAIT_TIME = min(300, 1.5 * WAIT_TIME)

    def _subscribe_topics(self):
        """Subscribe to modem specific topics."""
        pub.subscribe(self.connect, "connection.lost")

    def _register_states(self):
        """No states to register for modems."""

    def _register_default_links(self):
        """No default links for modems."""

    def _register_handlers(self):
        """Register command handlers for modems."""


class PLM(Modem):
    """Insteon PLM class."""

    def __init__(self, device, workdir=''):
        """Init the PLM class."""
        super().__init__(workdir)
        self._device = device

    async def async_connect(self):
        """Connect to the PLM ascynronously."""
        from ..protocol.serial_protocol import connect as serial_connect
        self._transport, self._protocol = await serial_connect(self._device)
        WAIT_TIME = .0001
        while not self.connected:
            await asyncio.sleep(WAIT_TIME)
            WAIT_TIME = min(300, 1.5 * WAIT_TIME)
