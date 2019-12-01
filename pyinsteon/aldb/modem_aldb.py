"""All-Link database for an Insteon Modem."""
from typing import Callable
import logging

from . import ALDBBase
from .aldb_version import ALDBVersion
from .aldb_status import ALDBStatus
from .aldb_record import ALDBRecord

_LOGGER = logging.getLogger(__name__)

class ModemALDB(ALDBBase):
    """All-Link database for modems.

    Subscribed topics:
    modem.aldb.loaded: Triggered when the ALDB load command completes.

    Messages sent:
    modem.aldb.load: Triggers the loading of the ALDB.
    """

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0000):
        """Init the ModemALDB."""
        from ..managers.im_read_manager import ImReadManager
        super().__init__(address, version, mem_addr)
        self._read_manager = ImReadManager(self)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._records[mem_addr] = record

    #pylint: disable=arguments-differ
    async def async_load(self, callback: Callable = None):
        """Load the All-Link Database."""
        _LOGGER.debug('Loading the modem ALDB')
        self._records = {}
        await self._read_manager.async_load()
        self._status = ALDBStatus.LOADED
        if callback:
            callback()
        return self._status
