"""All-Link database for battery oppertated devices."""
import logging
from collections import namedtuple

from ..constants import ALDBVersion
from . import ALDB

LoadCommandParams = namedtuple("LoadCommandParams", "mem_addr num_recs refresh")
Command = namedtuple("Command", "action params")

_LOGGER = logging.getLogger(__name__)


class ALDBBattery(ALDB):
    """ALDB for battery opperated devices."""

    def __init__(
        self, address, version=ALDBVersion.V2, mem_addr=0x0FFF, run_command=None
    ):
        """Init the ALDBBattery class."""
        super().__init__(address=address, version=version, mem_addr=mem_addr)
        self._commands = []
        self._run_command = run_command

    # pylint: disable=arguments-differ
    async def async_load(
        self,
        mem_addr: int = 0x00,
        num_recs: int = 0x00,
        refresh: bool = False,
    ):
        """Load the All-Link Database."""
        self._run_command(
            self.async_load_on_wake,
            mem_addr=mem_addr,
            num_recs=num_recs,
            refresh=refresh,
        )
        return True

    async def async_write(self, force=False):
        """Write modified records to the device."""
        self._run_command(self.async_write_on_wake, force=force)
        return 0

    async def async_load_on_wake(
        self,
        mem_addr: int = 0x00,
        num_recs: int = 0x00,
        refresh: bool = False,
    ):
        """Load the All-Link Database when the device wakes up."""
        return await super().async_load(
            mem_addr=mem_addr,
            num_recs=num_recs,
            refresh=refresh,
        )

    async def async_write_on_wake(self, force=False):
        """Write modified records to the device when the device wakes up."""
        return await super().async_write(force=force)
