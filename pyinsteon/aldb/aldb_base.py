"""Base class for the All-Link Database."""
import logging
from abc import ABC, abstractmethod

from .. import pub
from ..address import Address
from ..constants import ALDBStatus, ALDBVersion
from ..topics import (
    ALDB_VERSION,
    DEVICE_LINK_CONTROLLER_CREATED,
    DEVICE_LINK_CONTROLLER_REMOVED,
    DEVICE_LINK_RESPONDER_CREATED,
    DEVICE_LINK_RESPONDER_REMOVED,
)
from .aldb_record import ALDBRecord

_LOGGER = logging.getLogger(__name__)


class ALDBBase(ABC):
    """Represents a base class for a device All-Link database."""

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x0FFF):
        """Instantiate the ALL-Link Database object."""
        self._records = {}
        self._status = ALDBStatus.EMPTY
        self._version = version

        self._address = Address(address)
        self._mem_addr = mem_addr
        self._cb_aldb_loaded = None
        self._read_manager = None
        self._dirty_records = []
        pub.subscribe(self.update_version, f"{repr(self._address)}.{ALDB_VERSION}")

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return len(self._records)

    def __iter__(self):
        """Iterate through each ALDB device record."""
        for key in sorted(self._records, reverse=True):
            yield key

    def __getitem__(self, mem_addr):
        """Fetch a device from the ALDB."""
        return self._records.get(mem_addr)

    @abstractmethod
    def __setitem__(self, mem_addr, record):
        """Add or Update a device in the ALDB."""

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ", ".join("%s: %r" % item for item in attrs.items())

    @property
    def address(self) -> Address:
        """Returnt the status of the device."""
        return self._address

    @property
    def status(self) -> ALDBStatus:
        """Return the ALDB load status."""
        return self._status

    @property
    def version(self) -> ALDBVersion:
        """Return the ALDB version."""
        return self._version

    @property
    def first_mem_addr(self):
        """Return the expected memory address of the first record."""
        return self._mem_addr

    @property
    def high_water_mark_mem_addr(self):
        """Return the High Water Mark record memory address."""
        for mem_addr in self._records:
            record = self._records[mem_addr]
            if record.is_high_water_mark:
                return record.mem_addr
        return None

    @property
    def is_loaded(self) -> bool:
        """Test if the ALDB is loaded."""
        return self._status == ALDBStatus.LOADED

    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return self._records.get(mem_addr, default)

    def get_responders(self, group):
        """Return all responders to this device for a group."""
        for mem_addr in self._records:
            rec = self._records[mem_addr]
            if rec.is_controller and rec.group == group:
                yield rec.target

    def update_version(self, version):
        """Update the ALDB version number."""
        self._version = version

    @abstractmethod
    async def async_load(self, *args, **kwargs):
        """Load the All-Link Database."""

    def load_saved_records(self, status: ALDBStatus, records: [ALDBRecord]):
        """Load All-Link records from a dictionary of saved records."""
        if isinstance(status, ALDBStatus):
            self._status = status
        else:
            self._status = ALDBStatus(status)
        for mem_addr in records:
            record = records[mem_addr]
            self._notify_change(record, force_delete=True)
            self._records[mem_addr] = record
            self._notify_change(record)
        if self.is_loaded and self._records:
            keys = list(self._records.keys())
            keys.sort(reverse=True)
            self._mem_addr = keys[0]

    def _notify_change(self, record, force_delete=False):
        from .. import devices

        target = record.target
        group = record.group
        is_in_use = True if force_delete else record.is_in_use
        if group == 0 or target == devices.modem.address:
            return
        if record.is_controller and is_in_use:
            topic = DEVICE_LINK_CONTROLLER_CREATED
        elif record.is_controller and not is_in_use:
            topic = DEVICE_LINK_CONTROLLER_REMOVED
        elif not record.is_controller and is_in_use:
            topic = DEVICE_LINK_RESPONDER_CREATED
        else:
            topic = DEVICE_LINK_RESPONDER_REMOVED

        self._send_change(topic, self._address, target, group)

    @classmethod
    def _send_change(cls, topic, controller, responder, group):
        pub.sendMessage(topic, controller=controller, responder=responder, group=group)