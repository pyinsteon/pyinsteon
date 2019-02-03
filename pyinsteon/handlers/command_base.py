"""Command base object."""

from abc import ABCMeta, abstractmethod

class CommandBase(metaclass=ABCMeta):
    """Base class for all command types."""

    def __init__(self, manager, next_command):
        """Init the CommandBase class.

        manager: message manager container
        next_command: coroutine to execute next
        """
        self._manager = manager
        self._next_command = next_command

    @abstractmethod
    async def execute(self, **kwargs):
        """Execute the command."""
        raise NotImplementedError

    async def _run_next(self, **kwargs):
        if self._next_command:
            await self._next_command.execute(**kwargs)
        else:
            self._manager.complete(**kwargs)
