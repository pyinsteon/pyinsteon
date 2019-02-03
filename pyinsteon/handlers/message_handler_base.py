"""Base class to handle messages."""

from .command_base import CommandBase

class MessageHandlerBase(CommandBase):
    """Base class to handle messages."""

    def __init__(self, manager, msg, next_command, timeout=2):
        """Init the MessageHandlerBase class.

        manager: message manager container
        msg: Message to send or message template to process.
        next: coroutine to execute next
        timeout: Wait timeout max time in seconds
        """
        super().__init__(manager, next_command)
        self._msg = msg
        self._timeout = timeout