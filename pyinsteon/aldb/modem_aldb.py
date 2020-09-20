"""All-Link database for an Insteon Modem."""
import logging
from typing import Callable

from . import ALDBBase
from .. import pub
from ..constants import ALDBStatus, ALDBVersion, ManageAllLinkRecordAction
from ..handlers import ResponseStatus
from ..handlers.manage_all_link_record import ManageAllLinkRecordCommand
from ..managers.im_read_manager import ImReadManager
from ..topics import ALL_LINK_RECORD_RESPONSE

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 3


class ModemALDB(ALDBBase):
    """All-Link database for modems.

    Subscribed topics:
    modem.aldb.loaded: Triggered when the ALDB load command completes.

    Messages sent:
    modem.aldb.load: Triggers the loading of the ALDB.
    """

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x1FFF):
        """Init the ModemALDB."""

        super().__init__(address, version, mem_addr)

        # If we are not the first modem, don't subscribe to
        mgr = pub.getDefaultTopicMgr()
        topic = mgr.getTopic(ALL_LINK_RECORD_RESPONSE, okIfNone=True)
        if not topic:
            self._read_manager = ImReadManager(self)
        else:
            self._read_manager = None

        self._write_cmd = ManageAllLinkRecordCommand()

    # pylint: disable=arguments-differ
    async def async_load(self, callback: Callable = None):
        """Load the All-Link Database."""
        next_mem_addr = self.first_mem_addr
        _LOGGER.debug("Loading the modem ALDB")
        self._records = {}
        if self._read_manager is not None:
            # pylint: disable=not-an-iterable
            async for rec in self._read_manager.async_load():
                rec.mem_addr = next_mem_addr
                self._records[next_mem_addr] = rec
                next_mem_addr -= 8
        self._status = ALDBStatus.LOADED
        if callback:
            callback()
        return self._status

    async def _async_write_change(self, record):
        """Write a changed record."""
        if record.is_controller:
            action = ManageAllLinkRecordAction.MOD_FIRST_CTRL_OR_ADD
        else:
            action = ManageAllLinkRecordAction.MOD_FIRST_RESP_OR_ADD
        return await self._async_write_record(action, record)

    async def _async_write_delete(self, record):
        """Write a deleted record."""
        action = ManageAllLinkRecordAction.DELETE_FIRST
        return await self._async_write_record(action, record)

    async def _async_write_new(self, record):
        """Write a new record."""
        return await self._async_write_change(record)

    async def _async_write_record(self, action, record):
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
        return True
