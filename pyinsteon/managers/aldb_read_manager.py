"""ALDB Read Manager."""
import asyncio
import logging

import async_timeout

from ..aldb.aldb_record import ALDBRecord
from ..handlers.from_device.receive_aldb_record import ReceiveALDBRecordHandler
from ..handlers.to_device.read_aldb import ReadALDBCommandHandler

RETRIES_ALL_MAX = 5
RETRIES_ONE_MAX = 20
RETRIES_WRITE_MAX = 5
TIMER = 5
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

    async def async_read(self, mem_addr: int = 0x00, num_recs: int = 0):
        """Return an iterator of All-Link Database records."""
        _LOGGER.debug(
            "%s: Read memory %04x and %d records",
            str(self._aldb.address),
            mem_addr,
            num_recs,
        )
        self._clear_read_queue()

        try:
            async with async_timeout.timeout(TIMER_20_MIN):
                if _is_multiple_records(mem_addr, num_recs):
                    async for record in self._read_all():
                        yield record
                else:
                    record = await self._read_one(mem_addr)
                    if record is not None:
                        yield record
        except asyncio.TimeoutError:
            pass

    async def _read_one(self, mem_addr):
        """Read one record."""
        if self._aldb[mem_addr]:
            return None

        retries = RETRIES_ONE_MAX
        while retries:
            await self._read_handler.async_send(mem_addr=mem_addr, num_recs=1)

            timeout = TIMER + (RETRIES_ONE_MAX - retries) * TIMER_INCREMENT
            try:
                async with async_timeout.timeout(timeout):
                    record = await self._record_queue.get()
                    if record is not None and record.mem_addr == mem_addr:
                        return record
            except asyncio.TimeoutError:
                retries -= 1
                await asyncio.sleep(0.1)
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
                            return
                        yield record
            except asyncio.TimeoutError:
                retries -= 1
            if self._aldb.is_loaded:
                return
            await asyncio.sleep(0.1)

        # Read all records did not work so we try to read one at a time
        last_record = 0
        next_record = self._next_missing_record()
        while next_record is not None:
            record = await self._read_one(next_record)
            if record is not None:
                yield record

            last_record = next_record
            next_record = self._next_missing_record()

            # If the next record equals the last record and we believe we successfully
            # read the last record, an error occured so we should just stop
            if next_record == last_record:
                return

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
        self._record_queue.put_nowait(record)

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
