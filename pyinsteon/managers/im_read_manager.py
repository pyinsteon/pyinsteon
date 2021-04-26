"""Insteon Modem ALDB Read Manager."""
import asyncio
import logging

from .. import pub
from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..constants import ResponseStatus
from ..handlers.all_link_record_response import AllLinkRecordResponseHandler
from ..handlers.get_first_all_link_record import GetFirstAllLinkRecordHandler
from ..handlers.get_next_all_link_record import GetNextAllLinkRecordHandler
from ..topics import ALL_LINK_RECORD_RESPONSE

_LOGGER = logging.getLogger(__name__)


class ImReadManager:
    """Insteon Modem ALDB Read Manager."""

    def __init__(self, aldb):
        """Init the ImReadManager class."""
        self._aldb = aldb
        self._get_first_handler = GetFirstAllLinkRecordHandler()
        self._get_next_handler = GetNextAllLinkRecordHandler()
        mgr = pub.getDefaultTopicMgr()
        topic = mgr.getTopic(ALL_LINK_RECORD_RESPONSE, okIfNone=True)
        if not topic:
            self._receive_record_handler = AllLinkRecordResponseHandler()
            self._receive_record_handler.subscribe(self._receive_record)
        self._retries = 0
        self._load_lock = asyncio.Lock()
        self._record_queue = asyncio.Queue()

    def load(self):
        """Load the Insteon Modem ALDB."""
        asyncio.ensure_future(self.async_load())

    async def async_load(self):
        """Load the Insteon Modem ALDB."""
        asyncio.ensure_future(self._get_records())
        while True:
            rec = await self._record_queue.get()
            if rec is None:
                return
            yield rec

    async def _get_records(self):
        """Init the process to read records."""
        response = False
        retries = 3
        async with self._load_lock:
            while response != ResponseStatus.SUCCESS and retries:
                response = await self._get_first_handler.async_send()
                retries -= 1
            if response == ResponseStatus.SUCCESS:
                await self._get_next_record()
        self._record_queue.put_nowait(None)

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
        record = ALDBRecord(
            memory=0,
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
        self._record_queue.put_nowait(record)

    async def _get_next_record(self):
        """Get the next ALDB record."""
        response = ResponseStatus.FAILURE
        retries = 3
        unsent = 50
        while retries and unsent:
            response = await self._get_next_handler.async_send()
            if response == ResponseStatus.SUCCESS:
                retries = 3
                unsent = 50
            if response == ResponseStatus.FAILURE:
                retries -= 1
            if response == ResponseStatus.UNSENT:
                unsent -= 1
