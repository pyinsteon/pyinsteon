"""All-Link database for battery oppertated devices."""
import asyncio
from collections import namedtuple
from typing import Callable
from .. import pub
from . import ALDBVersion
from . import ALDB

LOAD_ACTION = 'load'
WRITE_ACTION = 'write'
CLOSE_ACTION = 'close'

LoadCommandParams = namedtuple('LoadCommandParams', 'mem_addr num_recs refresh callback')
Command = namedtuple('Command', 'action params')

class ALDBBattery(ALDB):
    """ALDB for battery opperated devices."""

    def __init__(self, address, version=ALDBVersion.v2, mem_addr=0x0fff):
        """Init the ALDBBattery class."""
        super().__init__(address=address, version=version, mem_addr=mem_addr)
        self._commands = []
        self._command_queue = asyncio.Queue()
        asyncio.ensure_future(self._wait_command())

    async def async_load(self, mem_addr: int = 0x00, num_recs: int = 0x00,
                         refresh: bool = False, callback: Callable = None):
        """Load the All-Link Database."""
        params = LoadCommandParams(mem_addr=mem_addr, num_recs=num_recs,
                                   refresh=refresh, callback=callback)
        cmd = Command(LOAD_ACTION, params)
        self._commands.append(cmd)
        return True

    async def async_write_records(self):
        """Write modified records to the device."""
        cmd = Command(WRITE_ACTION, None)
        self._commands.append(cmd)
        return True

    def close(self):
        """Close the wait command method."""
        cmd = Command(CLOSE_ACTION, None)
        self._command_queue.put_nowait(cmd)

    async def _wait_command(self):
        """Wait for a command."""
        while True:
            cmd = await self._command_queue.get()
            if cmd.action == LOAD_ACTION:
                p = cmd.params
                await super().async_load(mem_addr=p.mem_addr, num_recs=p.num_recs,
                                         refresh=p.refresh, callback=p.callback)
            elif cmd.action == WRITE_ACTION:
                await super().async_write_records()
            else:
                break

    def _wake_on_device(self, topic=pub.AUTO_TOPIC, **kwargs):
        """A device is awake and an action needs to be performed."""
        for cmd in self._commands:
            self._command_queue.put_nowait(cmd)
