"""Insteon Modem ALDB Read Manager."""
import asyncio
import logging
from ..handlers.get_first_all_link_record import GetFirstAllLinkRecordHandler
from ..handlers.get_next_all_link_record import GetNextAllLinkRecordHandler
from ..handlers.all_link_record_response import AllLinkRecordResponseHandler
from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..aldb.modem_aldb import ModemALDB
from ..constants import ResponseStatus


_LOGGER = logging.getLogger(__name__)


class ImReadManager:
    """Insteon Modem ALDB Read Manager."""

    def __init__(self, aldb: ModemALDB):
        """Init the ImReadManager class."""
        self._aldb = aldb
        self._get_first_handler = GetFirstAllLinkRecordHandler()
        self._get_next_handler = GetNextAllLinkRecordHandler()
        self._receive_record_handler = AllLinkRecordResponseHandler()
        self._receive_record_handler.subscribe(self._receive_record)
        self._retries = 0
        self._load_lock = asyncio.Lock()
        self._last_mem_addr = 0x0FFF

    def load(self):
        """Load the Insteon Modem ALDB."""
        asyncio.ensure_future(self.async_load())

    async def async_load(self):
        """Load the Insteon Modem ALDB."""
        response = False
        self._retries = 0
        await self._load_lock.acquire()
        while response != ResponseStatus.SUCCESS and not self._max_retries():
            response = await self._get_first_handler.async_send()
            self._retries += 1
        if response == ResponseStatus.SUCCESS:
            await self._load_lock.acquire()
        if self._load_lock.locked():
            self._load_lock.release()
        return ResponseStatus.SUCCESS

    def _max_retries(self):
        """Test if max retries reached."""
        return bool(self._retries >= 3)

    def _receive_record(
        self,
        in_use: bool,
        high_water_mark: bool,
        controller: bool,
        group: int,
        target: Address,
        data1: int,
        data2: int,
        data3: int,
        bit5: bool,
        bit4: bool,
    ):
        """Receive a record and load into the ALDB."""
        self._last_mem_addr = self._last_mem_addr - 8
        record = ALDBRecord(
            memory=self._last_mem_addr,
            controller=controller,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
            in_use=in_use,
            high_water_mark=high_water_mark,
            bit5=bit5,
            bit4=bit4,
        )
        self._aldb[self._last_mem_addr] = record
        asyncio.ensure_future(self._get_next_record())

    async def _get_next_record(self):
        """Get the next ALDB record."""
        response = ResponseStatus.FAILURE
        self._retries = 0
        while response != ResponseStatus.SUCCESS and not self._max_retries():
            # TODO check for success or failure
            response = await self._get_next_handler.async_send()
            self._retries += 1
        if self._max_retries() and self._load_lock.locked():
            self._load_lock.release()
