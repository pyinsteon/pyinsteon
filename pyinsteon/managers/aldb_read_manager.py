"""ALDB Read Manager."""
import asyncio
import logging

import async_timeout

from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..constants import ALDBStatus, ReadWriteMode, ResponseStatus
from ..data_types.all_link_record_flags import AllLinkRecordFlags
from ..handlers.from_device.receive_aldb_record import ReceiveALDBRecordHandler
from ..handlers.to_device.read_aldb import ReadALDBCommandHandler
from ..managers.peek_poke_manager import get_peek_poke_manager
from ..topics import ALDB_STATUS_CHANGED
from ..utils import subscribe_topic

RETRIES_ALL_MAX = 5
RETRIES_ONE_MAX = 20
TIMER_RECORD = 10
_LOGGER = logging.getLogger(__name__)


def _is_multiple_records(mem_addr, num_recs):
    """Return true if we are searching for multiple records."""
    return (mem_addr == 0x00 and num_recs == 0) or num_recs > 1


class ALDBReadManager:
    """ALDB Read Manager."""

    def __init__(self, address, first_record):
        """Init the ALDBReadManager class."""
        self._address = Address(address)
        self._first_record = first_record
        self._record_queue = asyncio.Queue()
        self._continue = True

        self._read_handler = ReadALDBCommandHandler(self._address)
        self._record_handler = ReceiveALDBRecordHandler(self._address)
        self._record_handler.subscribe(self._receive_record)

        self._peek_bytes_received = asyncio.Queue()
        self._peek_manager = get_peek_poke_manager(self._address)
        self._peek_manager.subscribe_peek(self._receive_peek)
        subscribe_topic(
            self._aldb_status_changed, f"{self._address.id}.{ALDB_STATUS_CHANGED}"
        )

    async def async_read(
        self,
        mem_addr: int = 0x00,
        num_recs: int = 0,
        read_write_mode=ReadWriteMode.STANDARD,
    ):
        """Return an iterator of All-Link Database records."""
        _LOGGER.debug(
            "%s: Read memory %04x and %d records",
            str(self._address),
            mem_addr,
            num_recs,
        )
        self._clear_read_queue()
        self._continue = True
        if read_write_mode == ReadWriteMode.PEEK_POKE:
            read_all_method = self._read_all_peek
            read_one_method = self._read_one_peek
        else:
            read_all_method = self._read_all
            read_one_method = self._read_one

        if _is_multiple_records(mem_addr, num_recs):
            async for record in read_all_method():
                _LOGGER.debug("Read manager returning: %s", str(record))
                yield record
                await asyncio.sleep(0.05)
        else:
            record = await read_one_method(mem_addr)
            if record is not None:
                _LOGGER.debug("Read manager returning: %s", str(record))
                yield record
                await asyncio.sleep(0.05)

        _LOGGER.debug("Read manager completed")

    async def async_stop(self):
        """Stop the reading process."""
        self._continue = False
        await self._record_queue.put(None)
        await asyncio.sleep(0.01)

    async def _read_one(self, mem_addr):
        """Read one record."""
        retries = RETRIES_ONE_MAX
        while retries and self._continue:
            response = await self._read_handler.async_send(
                mem_addr=mem_addr, num_recs=1
            )
            if response in [
                ResponseStatus.DIRECT_NAK_ALDB,
                ResponseStatus.DIRECT_NAK_INVALID_COMMAND,
                ResponseStatus.DIRECT_NAK_INVALID_COMMAND,
                ResponseStatus.DIRECT_NAK_CHECK_SUM,
            ]:
                # When Checksum direct NAK, should we change the checksum method?
                _LOGGER.error(
                    "Device refused the ALDB Read command with error: %s (%r)",
                    response,
                    response,
                )
                return None
            try:
                async with async_timeout.timeout(TIMER_RECORD):
                    record = await self._record_queue.get()
                    if record is not None and record.mem_addr == mem_addr:
                        _LOGGER.debug("_read_one returning record: %s", str(record))
                        return record
                    _LOGGER.debug("_read_one not returning record: %s", str(record))
            except asyncio.TimeoutError:
                retries -= 1
            await asyncio.sleep(0.1)
        _LOGGER.debug("_read_one completed")
        return None

    async def _read_one_peek(self, mem_addr):
        """Read one record using peek commands."""
        retries = RETRIES_ONE_MAX
        while retries:
            record = bytearray()
            for curr_byte in range(0, 8):
                value = await self._async_peek(mem_addr=mem_addr - curr_byte)
                if value is None:
                    break
                record.append(value)
            if len(record) == 8:
                flags = AllLinkRecordFlags(record[7])
                aldb_record = ALDBRecord(
                    memory=mem_addr,
                    controller=flags.is_controller,
                    group=record[6],
                    target=Address(bytearray([record[5], record[4], record[3]])),
                    data1=record[2],
                    data2=record[1],
                    data3=record[0],
                    in_use=flags.is_in_use,
                    high_water_mark=flags.is_hwm,
                    bit4=flags.is_bit_4_set,
                    bit5=flags.is_bit_5_set,
                )
                _LOGGER.info(str(aldb_record))
                return aldb_record
            retries -= 1
            _LOGGER.debug("Retrying reading record at 0x%04X", mem_addr)
        _LOGGER.debug("Read ONE return on error - incomplete reads")
        return None

    async def _async_peek(self, mem_addr):
        """Peek one byte."""
        _LOGGER.debug("Peeking memory address: 0x%04X", mem_addr)
        retries_byte = 20
        timeout = 3
        while retries_byte:
            while not self._peek_bytes_received.empty():
                await self._peek_bytes_received.get()
            result = await self._peek_manager.async_peek(mem_addr)
            if result == ResponseStatus.SUCCESS:
                try:
                    async with async_timeout.timeout(timeout):
                        peek_addr, value = await self._peek_bytes_received.get()
                        if mem_addr == peek_addr:
                            _LOGGER.debug(
                                "Returning value: %d for memory address: 0x%04X",
                                value,
                                mem_addr,
                            )
                            return value
                except asyncio.TimeoutError:
                    pass
            retries_byte -= 1
            _LOGGER.debug("Retrying byte at 0x%04X", mem_addr)
        return None

    async def _read_all(self):
        """Read all records."""
        retries = RETRIES_ALL_MAX
        while retries and self._continue:
            response = await self._read_handler.async_send(mem_addr=0, num_recs=0)
            if response in [
                ResponseStatus.DIRECT_NAK_ALDB,
                ResponseStatus.DIRECT_NAK_INVALID_COMMAND,
                ResponseStatus.DIRECT_NAK_CHECK_SUM,
            ]:
                # When Checksum direct NAK, should we change the checksum method?
                _LOGGER.error(
                    "Device refused the ALDB Read command with error: %s (%r)",
                    response,
                    response,
                )
                return
            try:
                while self._continue:
                    async with async_timeout.timeout(TIMER_RECORD):
                        record = await self._record_queue.get()
                        if record is None:
                            _LOGGER.debug("_read_all completed")
                            return
                        _LOGGER.debug("_read_all returning record: %s", str(record))
                        yield record
                        await asyncio.sleep(0.05)
            except asyncio.TimeoutError:
                retries -= 1

        _LOGGER.debug("_read_all completed")

    async def _read_all_peek(self):
        """Read all ALDB records using peek commands."""
        next_record = self._first_record
        while self._continue:
            record = await self._read_one_peek(next_record)
            if record is None:
                return
            yield record
            await asyncio.sleep(0.05)
            if record.is_high_water_mark:
                return
            await asyncio.sleep(0.06)  # let the ALDB catch up to changes
            next_record = next_record - 8

    async def _receive_record(
        self,
        memory,
        controller,
        group,
        target,
        data1,
        data2,
        data3,
        in_use,
        high_water_mark,
        bit5,
        bit4,
    ):
        """Receive an ALDB record."""
        record = ALDBRecord(
            memory=memory,
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
        _LOGGER.debug("Putting record in queue: %s", str(record))
        await self._record_queue.put(record)

    async def _receive_peek(self, mem_addr, value):
        """Receive one byte from a peek command."""
        _LOGGER.debug("Putting one byte from peek command")
        await self._peek_bytes_received.put((mem_addr, value))

    def _clear_read_queue(self):
        """Clear the read queue of old records."""

        while not self._record_queue.empty():
            self._record_queue.get_nowait()

    async def _aldb_status_changed(self, status):
        """Listen for status changes and stop the read if needed."""
        if self._continue and status == ALDBStatus.LOADED:
            self._continue = False
            await self._record_queue.put(None)
