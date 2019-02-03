"""Manage a series of messages and commands."""
from asyncio import Queue
from .command_base import CommandBase


class MessageManager(CommandBase):
    """Manage a message chain."""

    def __init__(self, manager, callback):
        """Init the MessageManager."""
        super().__init__(manager, None)
        self._callback = callback
        self._msg_queue = Queue()

    @property
    def msg_queue(self):
        """Return the message queue."""
        return self._msg_queue

    def add_handler(self, next_command):
        """Add the next command handler."""
        self._next_command = next_command

    async def execute(self, **kwargs):
        """Start the message chain."""
        await self._run_next(**kwargs)

    def complete(self, **kwargs):
        """Run callback after chain completes."""
        if self._callback:
            self._callback(**kwargs)

    def timeout(self, **kwargs):
        """Receive a timeout error.

        For now, this will do nothing.
        """
        print("Timeout exceeded.")

    def send(self, msg):
        """Send a message using the manager."""
        self._manager.send(msg)

    async def not_handled(self, **kwargs):
        """Recieve an unhandled message."""
        await self._run_next(**kwargs)
