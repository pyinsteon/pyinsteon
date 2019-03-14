"""Manage state value updates."""
from abc import ABCMeta, abstractmethod

from .command_base import CommandBase


class StateManager(CommandBase):
    """Update a state based on a message received."""

    __metaclass__ = ABCMeta

    def __init__(self, manager, state, next_command=None):
        """Init the StateManager class."""
        super().__init__(manager, next_command)
        self._state = state

    @abstractmethod
    async def execute(self, **kwargs):
        """Execute the state change."""
        raise NotImplementedError
