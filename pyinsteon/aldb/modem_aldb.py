"""All-Link database for an Insteon Modem."""
from typing import Callable
import logging

from . import ALDBBase
from .aldb_version import ALDBVersion
from .aldb_status import ALDBStatus
from .aldb_record import ALDBRecord
from ..address import Address

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 3


class ModemALDB(ALDBBase):
    """All-Link database for modems.

    Subscribed topics:
    modem.aldb.loaded: Triggered when the ALDB load command completes.

    Messages sent:
    modem.aldb.load: Triggers the loading of the ALDB.
    """

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x0000):
        """Init the ModemALDB."""
        from ..managers.im_read_manager import ImReadManager

        super().__init__(address, version, mem_addr)
        self._read_manager = ImReadManager(self)

    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""
        if not isinstance(record, ALDBRecord):
            raise ValueError

        self._records[mem_addr] = record

    # pylint: disable=arguments-differ
    async def async_load(self, callback: Callable = None):
        """Load the All-Link Database."""
        _LOGGER.debug("Loading the modem ALDB")
        self._records = {}
        await self._read_manager.async_load()
        self._status = ALDBStatus.LOADED
        if callback:
            callback()
        return self._status

    def add(
        self,
        group: int,
        target: Address,
        controller: bool,
        data1: int = 0,
        data2: int = 0,
        data3: int = 0,
    ):
        """Add a record to the All-Link database."""
        record = ALDBRecord(
            memory=0,
            in_use=True,
            controller=controller,
            high_water_mark=False,
            bit5=True,
            group=group,
            target=target,
            data1=data1,
            data2=data2,
            data3=data3,
        )
        self._dirty_records.append(record)

    def remove(self, controller, group, target):
        """Remove a record to the All-Link database."""
        record = ALDBRecord(
            memory=0,
            in_use=False,
            controller=controller,
            high_water_mark=False,
            bit5=True,
            group=group,
            target=target,
            data1=0,
            data2=0,
            data3=0,
        )
        self._dirty_records.append(record)

    async def async_write(self):
        """Write modified records to the device.

        Returns a tuple of (completed, failed) record counts.
        """
        from ..handlers.manage_all_link_record import ManageAllLinkRecordCommand
        from ..constants import ManageAllLinkRecordAction
        from ..handlers import ResponseStatus

        completed = []
        failed = []
        cmd = ManageAllLinkRecordCommand()
        self._id_recs_to_restore()
        while self._dirty_records:
            rec = self._dirty_records.pop()
            if not rec.is_in_use:
                action = ManageAllLinkRecordAction.DELETE_FIRST
            elif rec.is_controller:
                action = ManageAllLinkRecordAction.MOD_FIRST_CTRL_OR_ADD
            else:
                action = ManageAllLinkRecordAction.MOD_FIRST_RESP_OR_ADD
            retries = 0
            response = ResponseStatus.UNSENT
            while response != ResponseStatus.SUCCESS and retries < MAX_RETRIES:
                response = await cmd.async_send(
                    action=action,
                    controller=rec.is_controller,
                    group=rec.group,
                    target=rec.target,
                    data1=rec.data1,
                    data2=rec.data2,
                    data3=rec.data3,
                    in_use=rec.is_in_use,
                    high_water_mark=rec.is_high_water_mark,
                    bit5=rec.is_bit5_set,
                    bit4=rec.is_bit4_set,
                )
                retries += 1
            if response == ResponseStatus.SUCCESS:
                completed.append(rec)
            else:
                failed.append(rec)

        return len(completed), len(failed)

    def _id_recs_to_restore(self):
        """Find matching records to delete and restore.

        When deleting a record it is required to delete all that match the target and group
        then restore all the ones that do not match the controller. (yes it is stupid)
        """
        deleted_recs = []
        restore_recs = []
        multi_delete = []
        for rec in self._dirty_records:
            if not rec.is_in_use:
                deleted_recs.append(rec)

        for del_rec in deleted_recs:
            found_restore = False
            for mem_addr in self._records:
                rec = self._records[mem_addr]
                if rec.target == del_rec.target and rec.group == del_rec.group:
                    new_rec = self._set_not_in_use(rec)
                    multi_delete.append(new_rec)
                    if (
                        not rec.is_controller == del_rec.is_controller
                        and not found_restore
                    ):
                        # We only need one controller or responder for a target and group
                        restore_recs.append(rec)
        self._dirty_records.extend(multi_delete)
        self._dirty_records.extend(restore_recs)

    @classmethod
    def _set_not_in_use(cls, rec):
        new_rec = ALDBRecord(
            memory=rec.mem_addr,
            controller=rec.is_controller,
            group=rec.group,
            target=rec.target,
            data1=rec.data1,
            data2=rec.data2,
            data3=rec.data3,
            in_use=False,
            high_water_mark=False,
            bit4=True,
            bit5=False,
        )
        return new_rec
