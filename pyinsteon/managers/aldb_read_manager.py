"""ALDB Read Manager."""
import asyncio
import logging

from async_generator import async_generator, yield_

from ..aldb.aldb_record import ALDBRecord

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

    def __init__(self, aldb, mem_addr: int = 0x00, num_recs: int = 0):  # : ALDB):
        """Init the ALDBReadManager class."""
        from ..handlers.to_device.read_aldb import ReadALDBCommandHandler
        from ..handlers.from_device.receive_aldb_record import ReceiveALDBRecordHandler

        self._aldb = aldb
        self._mem_addr = mem_addr
        self._num_recs = num_recs

        self._records = asyncio.Queue()
        self._retries_all = 0
        self._retries_one = 0
        self._retries_write = 0
        self._last_command = None
        self._last_mem_addr = 0
        self._read_handler = ReadALDBCommandHandler(self._aldb.address)
        self._record_handler = ReceiveALDBRecordHandler(self._aldb.address)
        self._read_handler.subscribe(self._receive_direct_ack)
        self._record_handler.subscribe(self._receive_record)
        self._timer_lock = asyncio.Lock()

    @async_generator
    async def async_read(self, mem_addr: int = 0x00, num_recs: int = 0):
        """Start the reading process to enable iteration."""
        if self._mem_addr == 0x0000 and self._num_recs == 0:
            self._last_command = READ_ALL
        else:
            self._last_command = READ_ONE
        self._last_mem_addr = self._mem_addr
        await self._async_read(mem_addr=self._mem_addr, num_recs=self._num_recs)
        while True:
            record = await self._records.get()
            if record is None:
                break
            await yield_(record)

    async def _async_read(self, mem_addr: int = 0x00, num_recs: int = 0):
        """Perform the device read function."""
        if self._last_command == READ_ALL and self._retries_all < RETRIES_ALL_MAX:
            retries = self._retries_all
        else:
            retries = self._retries_one
        _LOGGER.debug("Attempting to read %x", mem_addr)
        # TODO check for success or failure
        await self._read_handler.async_send(mem_addr=mem_addr, num_recs=num_recs)
        timer = TIMER + retries * TIMER_INCREMENT
        asyncio.ensure_future(self._timer(timer, mem_addr, num_recs))

    def _receive_direct_ack(self, ack_response):
        """Receive the response from the direct ACK."""
        if ack_response in [
            IM_NOT_IN_DEVICE_ALDB,
            CHECKSUM_ERROR,
            ILLEGAL_VALUE_IN_COMMAND,
        ]:
            _LOGGER.error("ALDB Load error: 0x%02x", ack_response)
            self._last_command = CANCEL
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
        asyncio.ensure_future(self._release_timer())

    async def _release_timer(self):
        """Release the lock that tells `_timer` to quit."""
        if self._last_command == READ_ALL and self._retries_all < RETRIES_ALL_MAX:
            # Wait to see if more messages come in.
            await asyncio.sleep(5)
        if self._timer_lock.locked():
            self._timer_lock.release()

    async def _timer(self, timer, mem_addr, num_recs):
        """Set a timer to confirm if the last get command completed."""
        if self._timer_lock.locked():
            self._timer_lock.release()
        await self._timer_lock.acquire()
        try:
            await asyncio.wait_for(self._timer_lock.acquire(), timer)
        except asyncio.TimeoutError:
            pass
        if self._last_command == READ_ALL:
            self._manage_get_all_cmd(mem_addr, num_recs)
        elif self._last_command == READ_ONE:
            self._manage_get_one_cmd(mem_addr, num_recs)

    def _manage_get_all_cmd(self, mem_addr, num_recs):
        """Manage the READ_ALL command process."""
        _LOGGER.debug("In _manage_get_all_cmd")
        if self._aldb.calc_load_status():
            # The ALDB is fully loaded so stop
            self._records.put_nowait(None)
            return

        if self._retries_all < RETRIES_ALL_MAX:
            # Attempt to read all records again
            asyncio.ensure_future(self._async_read(0x0000, 0))
            self._retries_all += 1
            _LOGGER.info("Retry reading all records %d times", self._retries_all)
        else:
            # Read the next missing record
            next_mem_addr = self._next_missing_record()
            if next_mem_addr is None:
                # No records are missing so quit
                self._records.put_nowait(None)
                return
            if next_mem_addr == self._last_mem_addr:
                # We are still trying to get the same record as the last read
                if self._retries_one < RETRIES_ONE_MAX:
                    asyncio.ensure_future(self._async_read(next_mem_addr, 1))
                    self._retries_one += 1
                    _LOGGER.info(
                        "Retry reading 0x%04x record %d times",
                        next_mem_addr,
                        self._retries_one,
                    )
                else:
                    # Tried to read the same record max times so quit
                    self._records.put_nowait(None)
                    return
            else:
                # Reading a different record than the last attempt so reset
                # the retry count
                self._last_mem_addr = next_mem_addr
                self._retries_one = 0
                asyncio.ensure_future(self._async_read(next_mem_addr, 1))

    def _manage_get_one_cmd(self, mem_addr, num_recs):
        """Manage the READ_ONE command process."""
        if self._aldb.get(mem_addr):
            self._records.put_nowait(None)
            return
        if self._retries_one < RETRIES_ONE_MAX:
            asyncio.ensure_future(
                self._async_read(mem_addr=mem_addr, num_recs=num_recs)
            )
            self._retries_one += 1
            _LOGGER.info(
                "Retry reading 0x%04x record %d times", mem_addr, self._retries_one
            )
        else:
            # Trigger aldb.loaded but this will check the load status.
            self._records.put_nowait(None)
            return

    def _next_missing_record(self):
        last_addr = 0
        if not self._has_first_record():
            if self._last_mem_addr == 0x0000 and self._retries_one < RETRIES_ONE_MAX:
                return 0x0000
            return self._aldb.first_mem_addr
        for mem_addr in self._aldb:
            rec = self._aldb[mem_addr]
            if rec.is_high_water_mark:
                return None
            if last_addr != 0:
                if not last_addr - 8 == mem_addr:
                    return last_addr - 8
            last_addr = mem_addr
        return last_addr - 8

    def _has_first_record(self):
        """Test if the first record is loaded."""
        for mem_addr in self._aldb:
            if mem_addr in [self._aldb.first_mem_addr, 0x0FFF]:
                _LOGGER.debug("Found First record: 0x%04x", mem_addr)
                return True
        return False
