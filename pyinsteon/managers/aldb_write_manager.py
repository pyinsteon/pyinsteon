"""Manage writes to the All-Link Database."""
import asyncio
from typing import Tuple

from ..aldb.aldb_record import ALDBRecord
from ..constants import ResponseStatus
from ..handlers.to_device.write_aldb import WriteALDBCommandHandler


class ALDBWriteException(Exception):
    """All-Link Database write excetion."""


class ALDBWriteManager:
    """Manage writes to the All-Link Database."""

    def __init__(self, aldb):
        """Init the ALDBWriteManager class."""
        self._aldb = aldb
        self._address = aldb.address
        self._write_handler = WriteALDBCommandHandler(self._address)

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

        # If we get a direct ACK, we assume the ALDB has been written.
        # Should we force read to ensure it is accuate?
        resopnse_status = await self._write_handler.async_send(
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
        return resopnse_status
