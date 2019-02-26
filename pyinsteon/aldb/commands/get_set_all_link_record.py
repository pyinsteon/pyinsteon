"""Get, set or receive ALDB record."""
import asyncio
from enum import Enum
import logging

from ... import pub
from .. import ALDB
from ...address import Address
from ...messages.user_data import UserData
from ..aldb_record import ALDBRecord
from ..control_flags import ControlFlags

RETRIES_ALL_MAX = 5
RETRIES_ONE_MAX = 20
RETRIES_WRITE_MAX = 5
TIMER = 10
TIMER_INCREMENT = 3
_LOGGER = logging.getLogger(__name__)

class GetSetCmd(Enum):
    """Status of the command intention."""

    READ_ALL = 1
    READ_ONE = 2
    WRITE = 3


class GetSetAllLinkRecord():
    """Get, set or receive ALDB record."""

    def __init__(self, aldb: ALDB):
        """Init the ReceiveGetFirstAldbRecordNak class."""
        self._retries = 0
        self._aldb = aldb
        self._last_command: GetSetCmd
        self._last_mem_addr = 0

        self._subscribe_topics()

    #pylint: disable=no-self-use
    def read(self, mem_addr: int = 0x0000, num_recs: int = 0):
        """Get ALDB Records.

        Parameters:

        mem_addr: int (Default 0x0000) - Memory address of the record to retrieve.  When mem_addr
        is 0x0000 the device will return the first record.

        num_recs: int (Default 0)  Number of database records to return. When num_recs is 0 and
        mem_addr is 0x0000 the database will return all records.
        """
        self._retries = 0
        if mem_addr == 0x0000 and num_recs == 0:
            self._last_command = GetSetCmd.READ_ALL
        else:
            self._last_command = GetSetCmd.READ_ONE
        self._read(mem_addr, num_recs)

    def write(self, mem_addr: int, controller: bool, addr: Address,
              group: int = 0x00, data1: int = 0x00, data2: int = 0x00,
              data3: int = 0x00, in_use: bool = False,
              high_water_mark: bool = True, control_bit4: int = 0,
              control_bit5: int = 0):
        """Write an ALDB record.

        Parameters:
        - mem_addr: int - Memory address to write (ie. 0x0fff)
        - controller: bool - Is the current device a controller (True) or a responder (False)
        - addr: Address - Address of the remote device for this link record
        - group: int (Default 0) - group to control or respond to
        - data1: int (Default 0) - data 1 field value
        - data2: int (Default 0) - data 2 field value
        - data3: int (Default 0) - data 3 field value
        - in_use: bool (Default True) - Is the record in use (False is equal to delete)
        - high_water_mark: bool (Default False) - Is this the last record in the database
        - control_bit5: int (Defualt 0) - Control flags bit 4, device dependant
        - control_bit4: int (Defualt 0) - Control flags bit 4, device dependant
        """
        self._retries = 0
        self._last_command = GetSetCmd.WRITE
        control_flags = ControlFlags(in_use, controller, True,
                                     control_bit5, control_bit4)
        record = ALDBRecord(mem_addr, control_flags, group, addr,
                            data1, data2, data3)
        self._write(record)

    def _read(self, mem_addr: int, num_recs: int):
        from ...messages.outbound import send_extended
        from ...messages.message_flags import create as create_flags
        from ...constants import MessageFlagType
        flags = create_flags(MessageFlagType.DIRECT, True)
        num_recs = 0 if mem_addr == 0x0000 else 1
        mem_hi = mem_addr >> 8
        mem_lo = mem_addr & 0xff
        user_data = UserData({'d3': mem_hi, 'd4': mem_lo, 'd5': num_recs})
        user_data.set_checksum(0x2f, 0x00)
        msg = send_extended(self._aldb.address.id, flags, 0x2f, 0x00, user_data)
        pub.sendMessage('send.aldb.get{}'.format(self._aldb.address.id), msg=msg)

    def _write(self, record):
        from ...messages.outbound import send_extended
        from ...messages.message_flags import create as flags_create
        from ...constants import MessageFlagType
        flags = flags_create(MessageFlagType.DIRECT, True)
        user_data = UserData(dict(record))
        user_data.set_checksum(0x2f, 0x00)
        msg = send_extended(self._aldb.address.id, flags, 0x2f, 0x00, user_data)
        pub.sendMessage('send.aldb.write', msg=msg)

    def _receive_rec(self, cmd2: int, user_data: UserData = None):
        """Receive an All-Link record."""
        from ..aldb_record import create_from_userdata
        if not user_data:
            return  # This was a direct_ack so no user data is received.
        rec = create_from_userdata(user_data)
        self._aldb[rec.mem_addr] = rec

    def _receive_ack(self, cmd2: int, user_data: UserData = None):
        """receive the ACK message."""
        from ..aldb_record import create_from_userdata
        action = user_data.get('d2')
        num_recs = user_data.get('d5')
        record = create_from_userdata(user_data)
        timer = TIMER + self._retries * TIMER_INCREMENT

        if action == 0x00:
            asyncio.ensure_future(self._read_timer(timer, record.mem_addr, num_recs))
        else:
            asyncio.ensure_future(self._write_timer(timer, record))

    def _subscribe_topics(self):
        """Subscribe listeners to topics."""
        topic_recv_rec = '{}.read_write_aldb'.format(self._aldb.address.id)
        topic_get_rec = '{}.aldb.get'.format(self._aldb.address.id)
        topic_set_rec = '{}.aldb.set'.format(self._aldb.address.id)
        pub.subscribe(self._receive_rec, topic_recv_rec)
        pub.subscribe(self.read, topic_get_rec)
        pub.subscribe(self.write, topic_set_rec)
        pub.subscribe(self._receive_ack, 'ack.{}'.format(topic_recv_rec))

    async def _read_timer(self, timer, mem_addr, num_recs):
        """Set a timer to confirm if the last get command completed."""
        await asyncio.sleep(timer)
        if self._last_command == GetSetCmd.READ_ALL:
            self._manage_get_all_cmd(mem_addr, num_recs)
        else:
            self._manage_get_one_cmd(mem_addr, num_recs)

    async def _write_timer(self, timer, record):
        """Set a timer to confirm the last set command completed."""
        await asyncio.sleep(timer)
        if (not self._aldb.get(record.mem_addr) and
                self._retries < RETRIES_WRITE_MAX):
            self._write(record)

    def _manage_get_all_cmd(self, mem_addr, num_recs):
        """Manage the READ_ALL command process."""
        if self._aldb.is_loaded:
            return
        if self._retries < RETRIES_ALL_MAX:
            self._read(0x0000, 1)
            self._retries += 1
        elif not self._has_first_record:
            self._read(0x0000, 1)
            self._retries += 1
        else:
            next_mem_addr = self._next_missing_record()
            if next_mem_addr == self._last_mem_addr:
                if self._retries < RETRIES_ONE_MAX:
                    self._read(next_mem_addr, 1)
                    self._retries += 1
                elif self._last_mem_addr == 0x0000:
                    next_mem_addr = self._aldb.first_mem_addr
                    self._last_mem_addr = self._aldb.first_mem_addr
                    self._read(next_mem_addr, 1)
            else:
                self._last_mem_addr = next_mem_addr
                self._retries = 0
                self._read(next_mem_addr, num_recs)

    def _manage_get_one_cmd(self, mem_addr, num_recs):
        """Manage the READ_ONE command process."""
        if self._aldb.get(mem_addr):
            return

        if self._retries < RETRIES_ONE_MAX:
            pass

    def _next_missing_record(self):
        last_addr = 0
        if not self._has_first_record:
            return 0x0000
        for mem_addr in self._aldb:
            if last_addr != 0:
                if not last_addr  - 8 == mem_addr:
                    return last_addr - 8
            last_addr = mem_addr
        return last_addr - 8

    def _has_first_record(self):
        """Test if the first record is loaded."""
        if not self._aldb:
            return False

        found_first = False
        for mem_addr in self._aldb:
            if mem_addr == self._aldb.first_mem_addr or mem_addr == 0x0fff:
                found_first = True
        return found_first
