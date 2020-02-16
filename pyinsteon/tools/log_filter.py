"""Filter out command logging.

This is used by the stdout log so that it does not echo the command but the command is sent to the file log.
"""
from logging import Filter


class CommandFilter(Filter):
    """Filter out command logging."""

    def __init__(self, prompt):
        """Init the CommandFilter class."""
        super(CommandFilter, self).__init__()
        self.prompt = prompt

    def filter(self, record):
        """Filter out commands."""
        if record.msg[0 : len(self.prompt)] == self.prompt:
            return False
        return True
