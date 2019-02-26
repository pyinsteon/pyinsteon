"""Insteon Modem Base Class."""
from abc import ABCMeta, abstractmethod

from . import Device
from .. import pub
from ..protocol.serial_protocol import connect
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

    @abstractmethod
    async def connect(self):
        """Connect to the transport."""

    def _subscribe_topics(self):
        """Subscribe to modem specific topics."""
        pub.subscribe(self.connect(), "protocol.connection.lost")

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

    async def connect(self):
        """Connect to the PLM."""
        self._transport, self._protocol = await connect(self._device)
