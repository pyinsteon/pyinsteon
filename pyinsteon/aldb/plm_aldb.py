"""All-Link Database for PLM based devices."""
from .modem_aldb import ModemALDB
from ..address import Address
from .aldb_record import ALDBRecord

class PlmALDB(ModemALDB):
    """"All-Link database for PLM based devices."""

    def add(self, group: int, target: Address, controller: bool,
            data1: int = 0, data2: int = 0, data3: int = 0):
        """Add a record to the All-Link database."""
        record = ALDBRecord(memory=0, in_use=True, controller=controller, high_water_mark=False,
                            bit5=True, group=group, target=target,
                            data1=data1, data2=data2, data3=data3)
        self._dirty_records.append(record)

    async def async_write_records(self):
        """Write modified records to the device.

        Returns a tuple of (completed, failed) record counts.
        """
        from ..handlers.manage_all_link_record import ManageAllLinkRecordCommand
        from ..constants import ManageAllLinkRecordAction
        from ..handlers import ResponseStatus
        completed = []
        failed = []
        cmd = ManageAllLinkRecordCommand()
        while self._dirty_records:
            rec = self._dirty_records.pop()
            if rec.is_controller:
                action = ManageAllLinkRecordAction.MOD_FIRST_CTRL_OR_ADD
            else:
                action = ManageAllLinkRecordAction.MOD_FIRST_RESP_OR_ADD
            retries = 0
            response = ResponseStatus.UNSENT
            while response != ResponseStatus.SUCCESS and retries < 3:
                response = await cmd.async_send(
                    action=action, controller=rec.is_controller, group=rec.group,
                    target=rec.target, data1=rec.data1, data2=rec.data2, data3=rec.data3,
                    in_use=rec.is_in_use, high_water_mark=rec.is_high_water_mark,
                    bit5=rec.is_bit5_set, bit4=rec.is_bit4_set)
                retries += 1
            if response == ResponseStatus.SUCCESS:
                completed.append(rec)
            else:
                failed.append(rec)
        for rec in failed:
            self._dirty_records.append(rec)
        return len(completed), len(self._dirty_records)
