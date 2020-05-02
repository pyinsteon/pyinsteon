"""All-Link database for battery oppertated devices."""
import logging
from collections import namedtuple
from typing import Callable

from ..constants import ALDBVersion
from . import ALDB

LoadCommandParams = namedtuple(
    "LoadCommandParams", "mem_addr num_recs refresh callback"
)
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
        callback: Callable = None,
    ):
        """Load the All-Link Database."""
        self._run_command(
            super().async_load,
            mem_addr=mem_addr,
            num_recs=num_recs,
            refresh=refresh,
            callback=callback,
        )
        return True

    async def async_write(self, force=False):
        """Write modified records to the device."""
        self._run_command(super().async_write, force=force)
        return 0, 0
