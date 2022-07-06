"""All-Link database for an Insteon Modem."""
import logging

from pyinsteon.address import Address

from .. import pub
from ..constants import ALDBStatus, ALDBVersion, ReadWriteMode
from ..managers.aldb_im_read_manager import ImReadManager
from ..managers.aldb_im_write_manager import ImWriteManager
from ..topics import ALL_LINK_RECORD_RESPONSE
from . import ALDBBase

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 3


class ModemALDB(ALDBBase):
    """All-Link database for modems.

    Subscribed topics:
    modem.aldb.loaded: Triggered when the ALDB load command completes.

    Messages sent:
    modem.aldb.load: Triggers the loading of the ALDB.
    """

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x1FFF):
        """Init the ModemALDB."""

        super().__init__(address, version, mem_addr, write_manager=ImWriteManager)

        self._read_write_mode = ReadWriteMode.UNKNOWN
        # If we are not the first modem, don't subscribe to
        mgr = pub.getDefaultTopicMgr()
        topic = mgr.getTopic(ALL_LINK_RECORD_RESPONSE, okIfNone=True)
        if not topic:
            self._read_manager = ImReadManager(self)

    @property
    def read_write_mode(self) -> ReadWriteMode:
        """Emit the modem read mode."""
        return self._read_write_mode

    @read_write_mode.setter
    def read_write_mode(self, value: ReadWriteMode):
        """Set the modem read mode."""
        self._read_write_mode = ReadWriteMode(value)

    # pylint: disable=arguments-differ
    async def async_load(self, *args, **kwargs):
        """Load the All-Link Database."""

        if self._read_manager is None:
            return

        self._update_status(ALDBStatus.LOADING)
        # See if we can use EEPROM reads
        if self._read_write_mode == ReadWriteMode.UNKNOWN:
            top_of_mem = await self._read_manager.async_confirm_eeprom_read()
            if top_of_mem:
                self._mem_addr = top_of_mem
                self._read_write_mode = ReadWriteMode.EEPROM
            else:
                self._read_write_mode = ReadWriteMode.STANDARD

        _LOGGER.debug("Loading the modem ALDB: %s", self._read_write_mode)
        if self._read_write_mode == ReadWriteMode.EEPROM:
            await self._async_load_eeprom()
        else:
            await self._async_load_standard()
        self.set_load_status()

        return self._status

    async def async_find_records(self, address: Address, group: int):
        """Find an All-Link record in the Modem ALDB."""
        async for rec in self._read_manager.async_find(address, group):
            yield rec

    async def async_read_record(self, mem_addr):
        """Read from EEPROM."""
        return await self._read_manager.async_read_record(mem_addr=mem_addr)

    async def _async_load_standard(self):
        """Load using get first and get next methods."""
        next_mem_addr = self.first_mem_addr
        self._records = {}
        async for rec in self._read_manager.async_load_standard():
            rec.mem_addr = next_mem_addr
            self._records[next_mem_addr] = rec
            self._notify_change(rec)
            next_mem_addr -= 8

    async def _async_load_eeprom(self):
        """Load using EEPROM read method."""
        _LOGGER.debug("Loading from EEPROM")
        next_mem_addr = self.first_mem_addr
        self._records = {}
        record = await self._read_manager.async_read_record(next_mem_addr)
        while record:
            self._records[record.mem_addr] = record
            self._notify_change(record)
            if record.is_high_water_mark:
                return
            record = await self._read_manager.async_read_record(next_mem_addr)
            next_mem_addr -= 8

    def _calc_load_status(self):
        """Calculate the AlDB load status."""
        if self._read_write_mode == ReadWriteMode.STANDARD:
            return ALDBStatus.LOADED
        return super()._calc_load_status()
