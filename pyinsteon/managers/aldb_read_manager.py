"""ALDB Read Manager."""
import asyncio
import logging

from async_generator import async_generator, yield_

from ..aldb.aldb_record import ALDBRecord
from ..handlers.from_device.receive_aldb_record import ReceiveALDBRecordHandler
from ..handlers.to_device.read_aldb import ReadALDBCommandHandler

RETRIES_ALL_MAX = 5
RETRIES_ONE_MAX = 20
RETRIES_WRITE_MAX = 5
TIMER = 5
TIMER_INCREMENT = 3
_LOGGER = logging.getLogger(__name__)
READ_ALL = 1
READ_ONE = 2
WRITE = 3
CANCEL = 0

IM_NOT_IN_DEVICE_ALDB = 0xFF
CHECKSUM_ERROR = 0xFD
ILLEGAL_VALUE_IN_COMMAND = 0xFB


class ALDBReadManager:
    """ALDB Read Manager."""

    def __init__(self, aldb, mem_addr: int = 0x00, num_recs: int = 0):
        """Init the ALDBReadManager class."""
        self._aldb = aldb
        self._mem_addr = mem_addr
        self._num_recs = num_recs

        self._records = asyncio.Queue()
        self._retries_all = 0
        self._retries_one = 0
        self._command = None
        self._last_mem_addr = 0x0000
        self._read_handler = ReadALDBCommandHandler(self._aldb.address)
        self._record_handler = ReceiveALDBRecordHandler(self._aldb.address)
        self._read_handler.subscribe(self._receive_direct_ack)
        self._record_handler.subscribe(self._receive_record)
        self._timer_lock = asyncio.Lock()

    @async_generator
    async def async_read(self, mem_addr: int = 0x00, num_recs: int = 0):
        """Start the reading process to enable iteration."""
        self._init_read_process()
        if self._mem_addr == 0x0000 and self._num_recs == 0:
            self._command = READ_ALL
        else:
            self._command = READ_ONE

        await self._async_read(mem_addr=self._mem_addr, num_recs=self._num_recs)

        while True:
            record = await self._records.get()
            self._retries_one = 0
            if self._timer_lock.locked():
                self._timer_lock.release()
            if record is None:
                break
            await yield_(record)

    async def _async_read(self, mem_addr: int = 0x00, num_recs: int = 0):
        """Perform the device read function."""
        # TODO check for success or failure
        _LOGGER.debug(
            "%s: Read memory %04x and %d records",
            str(self._aldb.address),
            mem_addr,
            num_recs,
        )
        await self._read_handler.async_send(mem_addr=mem_addr, num_recs=num_recs)
        multiple_records = (mem_addr == 0x00 and num_recs == 0) or num_recs > 1
        if multiple_records:
            retries = self._retries_all
        else:
            retries = self._retries_one
        asyncio.ensure_future(
            self._wait_for_records(retries, multiple_records, mem_addr)
        )

    async def _wait_for_records(self, retries, multiple_records, last_addr):
        # Wait for timer to expire or records to be received.
        timer = max(TIMER + retries * TIMER_INCREMENT, 20)
        try:
            await asyncio.wait_for(self._timer_lock.acquire(), timer)
            # If we are reading multiple records continue waiting to see if more come in
            if multiple_records:
                await asyncio.sleep(10)
        except asyncio.TimeoutError:
            pass
        if self._timer_lock.locked():
            self._timer_lock.release()
        self._check_status(last_addr)

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

    def _check_status(self, last_mem_addr):
        """Check the status if the read process and trigger next step."""
        if self._command == READ_ALL:
            mem_addr = self._next_missing_record(last_mem_addr)
            if mem_addr is None:
                self._records.put_nowait(None)
                return

            if self._retries_all < RETRIES_ALL_MAX:
                asyncio.ensure_future(self._async_read(mem_addr=mem_addr, num_recs=0))
                self._retries_all += 1
                return

            if self._retries_one < RETRIES_ONE_MAX:
                asyncio.ensure_future(self._async_read(mem_addr=mem_addr, num_recs=1))
                self._retries_one += 1
                return

            self._records.put_nowait(None)
            return

        if self._retries_one < RETRIES_ONE_MAX:
            asyncio.ensure_future(
                self._async_read(mem_addr=self._mem_addr, num_recs=self._num_recs)
            )
            self._retries_one += 1
            return
        self._records.put_nowait(None)

    def _next_missing_record(self, last_mem_addr):
        prev_address = 0
        if not self._has_first_record():
            if last_mem_addr == 0x0000 and self._retries_one < RETRIES_ONE_MAX:
                return 0x0000
            return self._aldb.first_mem_addr

        for mem_addr in self._aldb:
            rec = self._aldb[mem_addr]
            if rec.is_high_water_mark:
                return None
            if prev_address != 0:
                if not prev_address - 8 == mem_addr:
                    return prev_address - 8
            prev_address = mem_addr
        next_addr = prev_address - 8
        return next_addr

    def _has_first_record(self):
        """Test if the first record is loaded."""
        for mem_addr in self._aldb:
            if mem_addr > 0x0FFF:
                return True
            if mem_addr in [self._aldb.first_mem_addr, 0x0FFF]:
                return True
        return False

    def _init_read_process(self):
        """Reinitialize the read process to ensure retries are correct."""
        self._retries_all = 0
        self._retries_one = 0
        self._command = None
        self._last_mem_addr = 0x0000
