"""Insteon Modem ALDB Read Manager."""
import asyncio
import logging

import async_timeout

from .. import pub
from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..constants import ManageAllLinkRecordAction, ResponseStatus
from ..handlers.all_link_record_response import AllLinkRecordResponseHandler
from ..handlers.get_first_all_link_record import GetFirstAllLinkRecordHandler
from ..handlers.get_next_all_link_record import GetNextAllLinkRecordHandler
from ..handlers.manage_all_link_record import ManageAllLinkRecordCommand
from ..handlers.read_eeprom import ReadEepromHandler
from ..handlers.read_eeprom_response import ReadEepromResponseHandler
from ..topics import ALL_LINK_RECORD_RESPONSE

_LOGGER = logging.getLogger(__name__)
TIMEOUT = 2


class ImReadManager:
    """Insteon Modem ALDB Read Manager."""

    def __init__(self, aldb):
        """Init the ImReadManager class."""
        self._aldb = aldb
        self._get_first_handler = GetFirstAllLinkRecordHandler()
        self._get_next_handler = GetNextAllLinkRecordHandler()
        self._find_cmd = ManageAllLinkRecordCommand()
        mgr = pub.getDefaultTopicMgr()
        topic = mgr.getTopic(ALL_LINK_RECORD_RESPONSE, okIfNone=True)
        if not topic:
            self._receive_record_handler = AllLinkRecordResponseHandler()
            self._receive_record_handler.subscribe(self._receive_record)
            self._receive_eeprom_record_handler = ReadEepromResponseHandler()
            self._receive_eeprom_record_handler.subscribe(self._receive_eeprom_record)
        self._retries = 0
        self._load_lock = asyncio.Lock()
        self._record_queue = asyncio.Queue()

    async def async_load_standard(self):
        """Load the Insteon Modem ALDB using standard method."""
        self._clear_read_queue()
        record = await self.async_get_first_all_link_record()
        if record:
            yield record
        else:
            return
        async for record in self.async_get_next_all_link_records():
            yield record

    async def async_load_eeprom(self):
        """Load the Insteon modem ALDB using EEPROM reads."""
        self._clear_read_queue()
        next_mem_addr = self._aldb.first_mem_addr
        record = await self.async_read_record(next_mem_addr)
        if record:
            yield record
        else:
            return
        for record in await self.async_read_record(next_mem_addr):
            yield record
            if record.is_high_water_mark:
                return
            next_mem_addr -= 8

    async def async_get_first_all_link_record(self):
        """Get the first All-Link database record."""
        self._clear_read_queue()
        retries = 3
        response = None
        while retries and response != ResponseStatus.SUCCESS:
            response = await self._get_first_handler.async_send()
            _LOGGER.debug("Get First Response: %s", response)
            retries -= 1

        if response == ResponseStatus.SUCCESS:
            try:
                async with async_timeout.timeout(TIMEOUT):
                    return await self._record_queue.get()
            except asyncio.TimeoutError:
                pass
        return None

    async def async_get_next_all_link_records(self):
        """Get the next All-Link database record."""
        self._clear_read_queue()
        retries = 3
        result = None
        while retries:
            result = await self._get_next_handler.async_send()
            retries -= 1

            if result == ResponseStatus.SUCCESS:
                try:
                    async with async_timeout.timeout(TIMEOUT):
                        yield await self._record_queue.get()
                except asyncio.TimeoutError:
                    pass
                else:
                    retries = 3
        return

    async def async_find(self, target, group):
        """Find one or more ALDB records."""
        self._clear_read_queue()
        record = await self._find_first_record(target=target, group=group)
        if record:
            yield record
        else:
            return
        async for record in self._find_next_records(target=target, group=group):
            yield record

    async def async_read_record(self, mem_addr: int) -> ALDBRecord:
        """Read from EEPROM."""
        self._clear_read_queue()
        retries = 20
        cmd = ReadEepromHandler()
        response = None
        while retries and response != ResponseStatus.SUCCESS:
            response = await cmd.async_send(mem_addr=mem_addr)
            retries -= 1
            if response == ResponseStatus.SUCCESS:
                try:
                    async with async_timeout.timeout(TIMEOUT):
                        return await self._record_queue.get()
                except asyncio.TimeoutError:
                    return None
            await asyncio.sleep(0.5)

    async def async_confirm_eeprom_read(self) -> int:
        """Confirm the first memory address is readable with an EEPROM read.

        Utilizes "get first aldb record" and "read eeprom" read methods to confirm
        the EEPROM method returns the same record as the standard modem read method.

        """
        mem_addrs = [0x1FFF, 0x3FFF]
        if self._aldb.first_mem_addr in mem_addrs:
            mem_addrs.remove(self._aldb.first_mem_addr)
        # Make the default memory address the first one we check
        mem_addrs.insert(0, self._aldb.first_mem_addr)

        self._clear_read_queue()
        async with self._load_lock:
            first_record = await self.async_get_first_all_link_record()
            eeprom_record = None
            for mem_addr in mem_addrs:
                eeprom_record = await self.async_read_record(mem_addr)
                if eeprom_record:
                    break

            if first_record is None and eeprom_record.is_high_water_mark:
                return eeprom_record.mem_addr  # ALDB is empty

            if first_record.is_exact_match(eeprom_record):
                return eeprom_record.mem_addr

            return 0

    async def _find_first_record(self, target, group):
        """Find the records in the background."""
        retries = 3
        response = None
        while retries and response != ResponseStatus.SUCCESS:
            response = await self._find_cmd.async_send(
                action=ManageAllLinkRecordAction.FIND_FIRST,
                controller=False,
                group=group,
                target=Address(target),
                data1=0,
                data2=0,
                data3=0,
                in_use=True,
                high_water_mark=False,
                bit5=0,
                bit4=0,
            )
            if response == ResponseStatus.SUCCESS:
                try:
                    async with async_timeout.timeout(TIMEOUT):
                        return await self._record_queue.get()
                except asyncio.TimeoutError:
                    pass
            retries -= 1

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

    def _receive_eeprom_record(
        self,
        mem_addr: int,
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
        """Receive an ALDB record from an EEPROM read."""
        record = ALDBRecord(
            memory=mem_addr,
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

    async def _find_next_records(self, target, group):
        """Find the next ALDB records."""
        response = ResponseStatus.FAILURE
        retries = 3
        unsent = 50
        while retries and unsent:
            response = await self._find_cmd.async_send(
                action=ManageAllLinkRecordAction.FIND_NEXT,
                controller=False,
                group=group,
                target=Address(target),
                data1=0,
                data2=0,
                data3=0,
                in_use=True,
                high_water_mark=False,
                bit5=0,
                bit4=0,
            )
            if response == ResponseStatus.SUCCESS:
                try:
                    async with async_timeout.timeout(TIMEOUT):
                        yield await self._record_queue.get()
                except asyncio.TimeoutError:
                    retries -= 1
                else:
                    retries = 3
                    unsent = 50
            elif response == ResponseStatus.UNSENT:
                unsent -= 1
            else:
                retries -= 1

        yield None

    def _clear_read_queue(self):
        """Clear the read queue of old records."""

        while not self._record_queue.empty():
            self._record_queue.get_nowait()
