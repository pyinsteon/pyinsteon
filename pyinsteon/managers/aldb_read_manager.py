"""ALDB Read Manager."""
import asyncio
import logging

import async_timeout

from ..address import Address
from ..aldb.aldb_record import ALDBRecord
from ..constants import ReadWriteMode, ResponseStatus
from ..data_types.all_link_record_flags import AllLinkRecordFlags
from ..handlers.from_device.receive_aldb_record import ReceiveALDBRecordHandler
from ..handlers.to_device.read_aldb import ReadALDBCommandHandler
from ..managers.peek_poke_manager import get_peek_poke_manager

RETRIES_ALL_MAX = 5
RETRIES_ONE_MAX = 20
RETRIES_WRITE_MAX = 5
TIMER = 10
TIMER_INCREMENT = 3
TIMER_20_MIN = 60 * 20
_LOGGER = logging.getLogger(__name__)
WRITE = 3
CANCEL = 0

IM_NOT_IN_DEVICE_ALDB = 0xFF
CHECKSUM_ERROR = 0xFD
ILLEGAL_VALUE_IN_COMMAND = 0xFB


def _is_multiple_records(mem_addr, num_recs):
    """Return true if we are searching for multiple records."""
    return (mem_addr == 0x00 and num_recs == 0) or num_recs > 1


class ALDBReadManager:
    """ALDB Read Manager."""

    def __init__(self, aldb):
        """Init the ALDBReadManager class."""
        self._aldb = aldb

        self._record_queue = asyncio.Queue()
        self._retries_all = RETRIES_ALL_MAX
        self._retries_one = RETRIES_ONE_MAX
        self._last_mem_addr = 0x0000
        self._read_handler = ReadALDBCommandHandler(self._aldb.address)
        self._record_handler = ReceiveALDBRecordHandler(self._aldb.address)
        self._read_handler.subscribe(self._receive_direct_ack_nak)
        self._record_handler.subscribe(self._receive_record)
        self._timer_lock = asyncio.Lock()
        self._peek_bytes_received = asyncio.Queue()
        self._peek_manager = get_peek_poke_manager(self._aldb.address)
        self._peek_manager.subscribe(self._receive_peek)

    async def async_read(self, mem_addr: int = 0x00, num_recs: int = 0, force=False):
        """Return an iterator of All-Link Database records."""
        _LOGGER.debug(
            "%s: Read memory %04x and %d records",
            str(self._aldb.address),
            mem_addr,
            num_recs,
        )
        self._clear_read_queue()

        if self._aldb.read_write_mode == ReadWriteMode.STANDARD:
            read_all_method = self._read_all
            read_one_method = self._read_one
        else:
            read_all_method = self._read_all_peek
            read_one_method = self._read_one_peek

        try:
            async with async_timeout.timeout(TIMER_20_MIN):
                if _is_multiple_records(mem_addr, num_recs):
                    async for record in self._read_all():
                        _LOGGER.debug("Read manager returning: %s", str(record))
                        yield record
                        await asyncio.sleep(0.05)
                else:
                    record = await self._read_one(mem_addr, force)
                    if record is not None:
                        _LOGGER.debug("Read manager returning: %s", str(record))
                        yield record
                        await asyncio.sleep(0.05)
        except asyncio.TimeoutError:
            pass
        _LOGGER.debug("Read manager completed")

    async def _read_one(self, mem_addr, force=False):
        """Read one record."""
        if self._aldb[mem_addr] and not force:
            _LOGGER.debug("_read_one completed")
            return None

        retries = RETRIES_ONE_MAX
        while retries:
            await self._read_handler.async_send(mem_addr=mem_addr, num_recs=1)

            timeout = TIMER + (RETRIES_ONE_MAX - retries) * TIMER_INCREMENT
            try:
                async with async_timeout.timeout(timeout):
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

        async def async_get_one_byte(mem_addr):
            retries_byte = 3
            timeout = 2
            while retries_byte:
                while not self._peek_bytes_received.empty():
                    await self._peek_bytes_received.get()
                result = await self._peek_manager.async_peek(mem_addr)
                if result == ResponseStatus.SUCCESS:
                    try:
                        async with async_timeout.timeout(timeout):
                            return await self._peek_bytes_received.get()
                    except asyncio.TimeoutError:
                        pass
                retries_byte -= 1
                await asyncio.sleep(0.1)
            return None

        if self._aldb[mem_addr]:
            return None

        retries = RETRIES_ONE_MAX
        while retries:
            record = bytearray()
            for curr_byte in range(0, 8):
                value = await async_get_one_byte(mem_addr=mem_addr - curr_byte)
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
        _LOGGER.info("Read ONE return on error - incomplete reads")
        return None

    async def _read_all(self):
        """Read all records."""
        if self._aldb.is_loaded:
            return

        retries = RETRIES_ALL_MAX
        while retries:
            await self._read_handler.async_send(mem_addr=0, num_recs=0)

            timeout = TIMER + (RETRIES_ALL_MAX - retries) * TIMER_INCREMENT
            try:
                while True:
                    async with async_timeout.timeout(timeout):
                        record = await self._record_queue.get()
                        if record is None:
                            _LOGGER.debug("_read_all completed")
                            return
                        _LOGGER.debug("_read_all returning record: %s", str(record))
                        yield record
                        await asyncio.sleep(0.1)
                    if self._aldb.is_loaded:
                        _LOGGER.debug("_read_all completed")
                        return
            except asyncio.TimeoutError:
                retries -= 1
            await asyncio.sleep(0.5)
            if self._aldb.is_loaded:
                _LOGGER.debug("_read_all completed")
                return

        # Read all records did not work so we try to read one at a time
        last_record = 0
        next_record = self._next_missing_record()
        while next_record is not None:
            record = await self._read_one(next_record)
            if record is not None:
                _LOGGER.debug("_read_all returning record: %s", str(record))
                yield record
                await asyncio.sleep(0.1)

            last_record = next_record
            next_record = self._next_missing_record()

            # If the next record equals the last record and we believe we successfully
            # read the last record, an error occured so we should just stop
            if next_record == last_record:
                _LOGGER.debug("_read_all completed")
                return
        _LOGGER.debug("_read_all completed")

    async def _read_all_peek(self):
        """Read all ALDB records using peek commands."""
        if self._aldb.is_loaded:
            return

        # Read all records did not work so we try to read one at a time
        last_record = 0
        next_record = self._next_missing_record()
        while next_record is not None:
            record = await self._read_one_peek(next_record)
            if record is not None:
                yield record
            await asyncio.sleep(0.05)  # let the ALDB catch up to changes
            last_record = next_record
            next_record = self._next_missing_record()

            # If the next record equals the last record and we believe we successfully
            # read the last record, an error occured so we should just stop
            if next_record == last_record:
                _LOGGER.info("Returning on error")
                return
        _LOGGER.info("Next record is NONE")

    def _receive_direct_ack_nak(self, response):
        """Receive the response from the direct NAK.

        The device has ackknowledged the request to read the ALDB.
        If the response is a negative response, stop the process.
        """
        if (response | 0xF0) in [
            IM_NOT_IN_DEVICE_ALDB,
            CHECKSUM_ERROR,
            ILLEGAL_VALUE_IN_COMMAND,
        ]:
            _LOGGER.error(
                "%s: ALDB Load error: 0x%02x", str(self._aldb.address), response
            )
            self._record_queue.put_nowait(None)

    def _receive_record(
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
        self._record_queue.put_nowait(record)

    async def _receive_peek(self, mem_addr, value):
        """Receive one byte from a peek command."""
        await self._peek_bytes_received.put(value)

    def _next_missing_record(self):
        if not self._has_first_record():
            return self._aldb.first_mem_addr

        next_addr = self._aldb.first_mem_addr
        for mem_addr in self._aldb:
            rec = self._aldb[mem_addr]
            if rec.is_high_water_mark:
                return None
            if not next_addr == mem_addr:
                return next_addr
            next_addr = mem_addr - 8

        return next_addr

    def _has_first_record(self):
        """Test if the first record is loaded."""
        for mem_addr in self._aldb:
            if mem_addr > 0x0FFF:
                return True
            if mem_addr in [self._aldb.first_mem_addr, 0x0FFF]:
                return True
        return False

    def _clear_read_queue(self):
        """Clear the read queue of old records."""

        while not self._record_queue.empty():
            self._record_queue.get_nowait()
