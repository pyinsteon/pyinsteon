"""All-Link Database for devices with no All-Link Database."""
from typing import Callable

from ..address import Address
from . import ALDBBase
from .aldb_status import ALDBStatus


class NoALDB(ALDBBase):
    """All-Link Database for devices with no All-Link Database."""

    def __setitem__(self, mem_addr, record):
        """Do nothing."""

    @property
    def is_loaded(self) -> bool:
        """Always returns loaded."""
        return ALDBStatus.LOADED

    #pylint: disable=arguments-differ
    async def async_load(self, mem_addr: int = 0x00, num_recs: int = 0x00,
                         refresh: bool = False, callback: Callable = None):
        """Load the All-Link Database."""
        if callback:
            callback()
        return ALDBStatus.LOADED

    async def async_write_records(self):
        """Write modified records to the device."""
        return 0

    def add(self, group: int, target: Address, controller: bool = False,
            data1: int = 0x00, data2: int = 0x00, data3: int = 0x00):
        """Add an All-Link record."""

    def remove(self, mem_addr: int):
        """Remove an All-Link record."""
