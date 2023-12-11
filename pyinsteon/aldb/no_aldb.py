"""All-Link Database for devices with no All-Link Database."""

from typing import List, Tuple

from ..address import Address
from ..constants import ALDBStatus, EngineVersion, ReadWriteMode, ResponseStatus
from .aldb_record import ALDBRecord


class NoALDB:
    """All-Link Database for devices with no All-Link Database."""

    def __init__(self, address: Address, version=EngineVersion.I2, mem_addr=0x0FFF):
        """Do nothing."""
        self._address = address

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return 0

    def __iter__(self):
        """Iterate through each ALDB device record."""
        for addr in {}:
            yield addr

    def __getitem__(self, mem_addr):
        """Fetch a device from the ALDB."""
        return {}

    def __setitem__(self, mem_addr, record):
        """Do nothing."""

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ", ".join(f"{k}: {repr(v)}" for k, v in attrs.items())

    def items(self):
        """Return the ALDB items."""
        return {}

    @property
    def address(self):
        """Returnt the status of the device."""
        return self._address

    @property
    def status(self) -> ALDBStatus:
        """Return loaded status."""
        return ALDBStatus.LOADED

    @property
    def version(self) -> EngineVersion:
        """Return the ALDB version."""
        return EngineVersion.UNKNOWN

    @property
    def first_mem_addr(self):
        """Return the expected memory address of the first record."""
        return 0x0FFF

    @property
    def high_water_mark_mem_addr(self) -> int:
        """Return the High Water Mark record memory address."""
        return 0x0FFF

    @property
    def is_loaded(self) -> bool:
        """Return loaded always."""
        return True

    @property
    def pending_changes(self):
        """Return pending changes."""
        return {}

    @property
    def read_write_mode(self) -> ReadWriteMode:
        """Emit the modem read mode."""
        return ReadWriteMode.STANDARD

    @read_write_mode.setter
    def read_write_mode(self, value: ReadWriteMode):
        """Set the modem read mode."""

    def clear(self):
        """Clear all records from the ALDB.

        This does not write to the device.
        """

    def clear_pending(self):
        """Remove pending changes."""

    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return None

    def get_responders(self, group):
        """Return all responders to this device for a group."""
        return None

    def update_version(self, version):
        """Update the ALDB version number."""

    def subscribe_status_changed(self, listener):
        """Subscribe to notification of ALDB load status changes."""

    def subscribe_record_changed(self, listener):
        """Subscribe to notification of ALDB record changes."""

    def unsubscribe_status_changed(self, listener):
        """Unsubscribe to notification of ALDB load status changes."""

    def unsubscribe_record_changed(self, listener):
        """Unsubscribe to notification of ALDB record changes."""

    async def async_load(self, *args, **kwargs):
        """Load the All-Link Database."""

    def load_saved_records(self, *args, **kwargs):
        """Load All-Link records from a dictionary of saved records."""

    def add(self, *args, **kwargs):
        """Add an All-Link record.

        This method does not write to the device. To write modifications to the device
        use `write` or `async_write`.
        """

    def remove(self, *args, **kwargs):
        """Remove an All-Link record."""

    def modify(self, *args, **kwargs):
        """Modify an All-Link record."""

    async def async_write(self, *args, **kwargs) -> Tuple[int, int]:
        """Write the dirty records to the device."""
        return ResponseStatus.SUCCESS, 0

    def find(self, *args, **kwargs) -> List[ALDBRecord]:
        """Find all records matching the criteria."""
        for no_recs in ():
            yield no_recs

    def set_load_status(self):
        """Review the ALDB records and identify the load status."""
