"""Manage writes to the All-Link Database."""
import asyncio
from typing import Tuple

from ..aldb.aldb_record import ALDBRecord
from ..constants import ReadWriteMode, ResponseStatus
from ..handlers.to_device.write_aldb import WriteALDBCommandHandler
from ..managers.peek_poke_manager import get_peek_poke_manager


class ALDBWriteException(Exception):
    """All-Link Database write excetion."""


class ALDBWriteManager:
    """Manage writes to the All-Link Database."""

    def __init__(self, aldb):
        """Init the ALDBWriteManager class."""
        self._aldb = aldb
        self._address = aldb.address
        self._write_handler = WriteALDBCommandHandler(self._address)
        self._poke_manager = get_peek_poke_manager(self._aldb.address)

    @property
    def can_write(self):
        """Return if the ALDB is loaded and we can write to it."""
        return self._aldb.is_loaded

    def write(self, record: ALDBRecord):
        """Write the ALDB record."""
        asyncio.ensure_future(self.async_write(record))

    async def async_write(
        self, record: ALDBRecord, force: bool = False
    ) -> Tuple[ResponseStatus, ALDBRecord]:
        """Write the ALDB record."""

        if not self.can_write and not force:
            raise ALDBWriteException(
                "All-Link databased must be loaded before writing."
            )

        if self._aldb.read_write_mode == ReadWriteMode.PEEK_POKE:
            return await self._poke_record(record)
        return await self._write_handler.async_send(
            mem_addr=record.mem_addr,
            controller=record.is_controller,
            group=record.group,
            target=record.target,
            data1=record.data1,
            data2=record.data2,
            data3=record.data3,
            in_use=record.is_in_use,
            bit5=record.is_bit5_set,
            bit4=record.is_bit4_set,
        )

    async def _poke_record(self, record: ALDBRecord):
        """Write the record using poke commands."""

        rec_bytes = bytearray(
            [
                record.data3,
                record.data2,
                record.data1,
                record.target.low,
                record.target.middle,
                record.target.high,
                record.group,
                record.control_flags,
            ]
        )
        mem_addr = record.mem_addr
        for curr_byte in range(0, 8):
            result = await self._async_write_byte(
                mem_addr - curr_byte, rec_bytes[curr_byte]
            )
            if result != ResponseStatus.SUCCESS:
                return result
        return ResponseStatus.SUCCESS

    async def _async_write_byte(self, mem_addr, value):
        """Write the byte to memory."""
        retries = 5
        while retries:
            result = await self._poke_manager.async_poke(mem_addr=mem_addr, value=value)
            if result == ResponseStatus.SUCCESS:
                return ResponseStatus.SUCCESS
            retries -= 1
        return ResponseStatus.FAILURE
