"""ALDB Read Manager."""
import asyncio
import logging

from ..aldb.aldb_record import ALDBRecord
from ..handlers.from_device.receive_aldb_record import ReceiveALDBRecordHandler
from ..handlers.to_device.read_aldb import ReadALDBCommandHandler

RETRIES_ALL_MAX = 5
RETRIES_ONE_MAX = 20
RETRIES_WRITE_MAX = 5
TIMER = 5
TIMER_INCREMENT = 3
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

    def __init__(self, aldb, mem_addr: int = 0x00, num_recs: int = 0):
        """Init the ALDBReadManager class."""
        self._aldb = aldb
        self._mem_addr = mem_addr
        self._num_recs = num_recs

        self._records = asyncio.Queue()
        self._records_to_return = asyncio.Queue()
        self._retries_all = RETRIES_ALL_MAX
        self._retries_one = RETRIES_ONE_MAX
        self._last_mem_addr = 0x0000
        self._read_handler = ReadALDBCommandHandler(self._aldb.address)
        self._record_handler = ReceiveALDBRecordHandler(self._aldb.address)
        self._read_handler.subscribe(self._receive_direct_ack)
        self._record_handler.subscribe(self._receive_record)
        self._timer_lock = asyncio.Lock()

    async def async_read(self, mem_addr: int = 0x00, num_recs: int = 0):
        """Start the reading process to enable iteration."""
        asyncio.ensure_future(
            self._async_read(mem_addr=self._mem_addr, num_recs=self._num_recs)
        )

        while True:
            record = await self._records_to_return.get()
            if record is None:
                return
            yield record

    async def _async_read(self, mem_addr: int = 0x00, num_recs: int = 0):
        """Perform the device read function."""
        # TODO check for success or failure
        _LOGGER.debug(
            "%s: Read memory %04x and %d records",
            str(self._aldb.address),
            mem_addr,
            num_recs,
        )

        if _is_multiple_records(mem_addr, num_recs):
            await self._read_all()
        else:
            await self._read_one(mem_addr)
        self._records_to_return.put_nowait(None)

    async def _read_one(self, mem_addr):
        """Read one record."""
        if self._aldb[mem_addr]:
            return True

        retries = RETRIES_ONE_MAX
        while retries:
            await self._read_handler.async_send(mem_addr=mem_addr, num_recs=1)

            timeout = TIMER + (RETRIES_ONE_MAX - retries) * TIMER_INCREMENT
            try:
                record = await self._get_next_record(timeout)
                if record is None:
                    return False
                if record.mem_addr == mem_addr:
                    return True
                await asyncio.sleep(0.1)
            except asyncio.TimeoutError:
                pass
            retries -= 1
        return False

    async def _read_all(self):
        """Read all records."""
        if self._aldb.is_loaded:
            return True

        retries = RETRIES_ALL_MAX
        while retries:
            await self._read_handler.async_send(mem_addr=0, num_recs=0)

            timeout = TIMER + (RETRIES_ALL_MAX - retries) * TIMER_INCREMENT
            try:
                while True:
                    record = await self._get_next_record(timeout)
                    if record is None:
                        return False
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.1)
            if self._aldb.is_loaded:
                return True
            retries -= 1

        # Read all records did not work so we try to read one at a time
        last_record = 0
        next_record = self._next_missing_record(last_record)
        while next_record is not None:
            if not await self._read_one(next_record):
                return False

            last_record = next_record
            next_record = self._next_missing_record(last_record)
            # If the next record equals the last record and we believe we successfully
            # read the last record, an error occured so we should just stop
            if next_record == last_record:
                return False
        return next_record is None

    async def _get_next_record(self, timeout):
        """Get the next record from the queue."""
        return await asyncio.wait_for(self._records.get(), timeout=timeout)

    def _receive_direct_ack(self, ack_response):
        """Receive the response from the direct ACK.

        The device has ackknowledged the request to read the ALDB.
        If the response is a negative response, stop the process.
        """
        if ack_response in [
            IM_NOT_IN_DEVICE_ALDB,
            CHECKSUM_ERROR,
            ILLEGAL_VALUE_IN_COMMAND,
        ]:
            _LOGGER.error(
                "%s: ALDB Load error: 0x%02x", str(self._aldb.address), ack_response
            )
            self._records.put_nowait(None)
            self._records_to_return.put_nowait(None)

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
        self._records.put_nowait(record)
        self._records_to_return.put_nowait(record)

    def _next_missing_record(self, last_mem_addr):
        prev_addr = 0
        if not self._has_first_record():
            if last_mem_addr == 0x0000 and self._retries_one < RETRIES_ONE_MAX:
                return 0x0000
            return self._aldb.first_mem_addr

        for mem_addr in self._aldb:
            rec = self._aldb[mem_addr]
            if rec.is_high_water_mark:
                return None
            if prev_addr != 0:
                if not prev_addr - 8 == mem_addr:
                    return prev_addr - 8
            prev_addr = mem_addr
        next_addr = prev_addr - 8
        if (
            self._aldb.high_water_mark_mem_addr
            and next_addr <= self._aldb.high_water_mark_mem_addr
        ):
            return None
        return next_addr

    def _has_first_record(self):
        """Test if the first record is loaded."""
        for mem_addr in self._aldb:
            if mem_addr > 0x0FFF:
                return True
            if mem_addr in [self._aldb.first_mem_addr, 0x0FFF]:
                return True
        return False
