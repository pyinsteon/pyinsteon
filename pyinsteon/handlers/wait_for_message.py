"""Wait for a message until timeout then execute a command."""

from asyncio import TimeoutError, wait_for

from .receive_message import ReceiveMessage


class WaitForMessage(ReceiveMessage):
    """Wait for next message in the chain."""
    
    async def execute(self, **kwargs):
        """Start a timer for the next message."""
        try:
            msg = await wait_for(self._manager.msg_queue.get(), self._timeout)
            if self._can_handle(msg=msg):
                await self._run_next(msg=msg)
        except TimeoutError:
            self._manager.timeout(handler=self, **kwargs)
