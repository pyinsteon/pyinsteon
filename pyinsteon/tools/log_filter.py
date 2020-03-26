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


class StdoutFilter(Filter):
    """Allow output to standard out."""

    def __init__(self, prefix):
        """Init the CommandFilter class."""
        super(StdoutFilter, self).__init__()
        self.prefix = prefix

    def filter(self, record):
        """Filter out commands."""
        if record.msg[0 : len(self.prefix)] == self.prefix:
            record.msg = self.strip_prefix(record.msg)
            return True
        return False

    def strip_prefix(self, msg):
        """Strip the prefix from the log message before writing out."""
        return msg[len(self.prefix) :]
