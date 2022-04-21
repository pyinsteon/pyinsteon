"""Manage the ALDB write process for an Insteon Modem."""

import logging
from typing import Tuple

from ..aldb.aldb_record import ALDBRecord
from ..constants import ManageAllLinkRecordAction, ReadWriteMode, ResponseStatus
from ..handlers.manage_all_link_record import ManageAllLinkRecordCommand
from ..handlers.write_eeprom import WriteEepromHandler
from .aldb_write_manager import ALDBWriteException

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 5


class ImWriteManager:
    """Manage writes to the Insteon Modem All-Link Database."""

    def __init__(self, aldb):
        """Init the ImWriteManager."""
        self._write_cmd = ManageAllLinkRecordCommand()
        self._aldb = aldb

    @property
    def can_write(self):
        """Return true if the AlDB is loaded."""
        return self._aldb.is_loaded

    async def async_write(
        self, record, force=False
    ) -> Tuple[ResponseStatus, ALDBRecord]:
        """Write a record to the ALDB."""

        if not self.can_write and not force:
            raise ALDBWriteException(
                "All-Link databased must be loaded before writing."
            )
        if self._aldb.read_write_mode == ReadWriteMode.EEPROM:
            return await self.async_write_record(record)

        if not record.is_in_use:
            return await self._async_write_delete_standard(record)

        return await self._async_write_change_standard(record)

    # pylint: disable=no-self-use
    async def async_write_record(self, record: ALDBRecord):
        """Write to EEPROM."""
        cmd = WriteEepromHandler()
        retries = 5
        result = ResponseStatus.UNSENT
        while retries and result != ResponseStatus.SUCCESS:
            result = await cmd.async_send(
                mem_addr=record.mem_addr,
                controller=record.is_controller,
                group=record.group,
                target=record.target,
                data1=record.data1,
                data2=record.data2,
                data3=record.data3,
                in_use=record.is_in_use,
                high_water_mark=record.is_high_water_mark,
                bit5=record.is_bit5_set,
                bit4=record.is_bit4_set,
            )
            retries -= 1
        return result

    async def _async_write_change_standard(
        self, record: ALDBRecord
    ) -> Tuple[ResponseStatus, ALDBRecord]:
        """Write a changed record."""
        curr_record = self._aldb.get(record.mem_addr, record)

        # Cannot change a controller to a responder or vise versa so delete first
        if curr_record.is_controller != record.is_controller:
            await self._async_write_delete_standard(curr_record)
            curr_record = record

        if curr_record.is_controller:
            action = ManageAllLinkRecordAction.MOD_FIRST_CTRL_OR_ADD
        else:
            action = ManageAllLinkRecordAction.MOD_FIRST_RESP_OR_ADD

        result = await self._async_write_record_standard(action, record)

        # If the record is already identical to `record` the modem returns a NAK
        # So test if a matching record is in the modem's ALDB
        if result != ResponseStatus.SUCCESS:
            if await self._find_matching_record(record):
                return ResponseStatus.SUCCESS
        return result

    async def _async_write_delete_standard(
        self, record
    ) -> Tuple[ResponseStatus, ALDBRecord]:
        """Write a deleted record."""
        matching_recs = await self._aldb.async_find_records(
            target=record.target, group=record.group
        )
        rec_to_delete = None
        for rec in matching_recs:
            if rec.is_controller == record.is_controller:
                rec_to_delete = rec
                break
        if rec_to_delete:
            return self._async_write_record_standard(
                rec_to_delete, ManageAllLinkRecordAction.DELETE_FIRST
            )

    async def _async_write_record_standard(
        self, action, record
    ) -> Tuple[ResponseStatus, ALDBRecord]:
        """Perform the ALDB write action."""
        retries = 0
        response = ResponseStatus.UNSENT
        while response != ResponseStatus.SUCCESS and retries < MAX_RETRIES:
            response = await self._write_cmd.async_send(
                action=action,
                controller=record.is_controller,
                group=record.group,
                target=record.target,
                data1=record.data1,
                data2=record.data2,
                data3=record.data3,
                in_use=record.is_in_use,
                high_water_mark=record.is_high_water_mark,
                bit5=record.is_bit5_set,
                bit4=record.is_bit4_set,
            )
            retries += 1

        return response

    async def _find_matching_record(self, record):
        """Find a matching record in the ALDB."""
        async for rec in self._aldb.async_find_records(record.target, record.group):
            if (
                rec.is_controller == record.is_controller
                and rec.data1 == record.data1
                and rec.data2 == record.data2
                and rec.data3 == record.data3
            ):
                return rec
        return None
