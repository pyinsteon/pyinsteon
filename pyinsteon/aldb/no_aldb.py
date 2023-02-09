"""All-Link Database for devices with no All-Link Database."""
from ..address import Address
from ..constants import ALDBStatus, EngineVersion, ReadWriteMode


class NoALDB:
    """All-Link Database for devices with no All-Link Database."""

    def __init__(self, address, version=EngineVersion.I2, mem_addr=0x0FFF):
        """Do nothing."""
        self._address = address

    def __setitem__(self, mem_addr, record):
        """Do nothing."""

    def __iter__(self):
        """Iterate through each ALDB device record."""
        for addr in {}:
            yield addr

    def __getitem__(self, mem_addr):
        """Fetch a device from the ALDB."""
        return {}

    def __len__(self):
        """Return the number of devices in the ALDB."""
        return 0

    def __repr__(self):
        """Human representation of a device from the ALDB."""
        attrs = vars(self)
        return ", ".join(f"{k}: {repr(v)}" for k, v in attrs.items())

    @property
    def is_loaded(self) -> bool:
        """Return loaded always."""
        return True

    @property
    def status(self) -> ALDBStatus:
        """Return loaded status."""
        return ALDBStatus.LOADED

    @property
    def read_write_mode(self) -> ReadWriteMode:
        """Emit the modem read mode."""
        return ReadWriteMode.STANDARD

    @read_write_mode.setter
    def read_write_mode(self, value: ReadWriteMode):
        """Set the modem read mode."""

    # pylint: disable=arguments-differ, no-self-use
    async def async_load(
        self,
        mem_addr: int = 0x00,
        num_recs: int = 0x00,
        refresh: bool = False,
    ):
        """Load the All-Link Database."""
        return ALDBStatus.LOADED

    # pylint: disable=no-self-use
    async def async_write(self):
        """Write modified records to the device."""
        return 0, 0

    def add(
        self,
        group: int,
        target: Address,
        controller: bool = False,
        data1: int = 0x00,
        data2: int = 0x00,
        data3: int = 0x00,
    ):
        """Add an All-Link record."""

    def remove(self, mem_addr: int):
        """Remove an All-Link record."""

    @property
    def address(self):
        """Returnt the status of the device."""
        return self._address

    @property
    def version(self) -> EngineVersion:
        """Return the ALDB version."""
        return EngineVersion.UNKNOWN

    @property
    def first_mem_addr(self):
        """Return the expected memory address of the first record."""
        return 0x0FFF

    @property
    def high_water_mark_mem_addr(self):
        """Return the High Water Mark record memory address."""
        return None

    # pylint: disable=no-self-use
    def get(self, mem_addr, default=None):
        """Get the record at address 'mem_addr'."""
        return None

    # pylint: disable=no-self-use
    def get_responders(self, group):
        """Return all responders to this device for a group."""
        return None

    def update_version(self, version):
        """Update the ALDB version number."""

    def load_saved_records(self, status, records, first_mem_addr):
        """Load All-Link records from a dictionary of saved records."""

    def find(self, *args, **kwargs):
        """Return no records."""
        return []
