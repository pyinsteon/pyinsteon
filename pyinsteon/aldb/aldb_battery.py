"""All-Link database for battery oppertated devices."""
from collections import namedtuple
from typing import Callable
from .. import pub
from . import ALDBVersion
from . import ALDB

LoadCommandParams = namedtuple(
    "LoadCommandParams", "mem_addr num_recs refresh callback"
)
Command = namedtuple("Command", "action params")


class ALDBBattery(ALDB):
    """ALDB for battery opperated devices."""

    def __init__(self, address, version=ALDBVersion.V2, mem_addr=0x0FFF):
        """Init the ALDBBattery class."""
        super().__init__(address=address, version=version, mem_addr=mem_addr)
        self._commands = []
        self._load_topic = "{}.aldb.load".format(self._address.id)
        self._write_topic = "{}.aldb.write".format(self._address.id)

    async def async_load(
        self,
        mem_addr: int = 0x00,
        num_recs: int = 0x00,
        refresh: bool = False,
        callback: Callable = None,
    ):
        """Load the All-Link Database."""
        pub.sendMessage(
            self._load_topic,
            mem_addr=mem_addr,
            num_recs=num_recs,
            refresh=refresh,
            callback=callback,
        )
        return True

    async def async_write_records(self):
        """Write modified records to the device."""
        pub.sendMessage(self._write_topic)
        return True
